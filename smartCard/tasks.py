from linecache import cache
from celery import shared_task
import pandas as pd
import requests
from django.utils import timezone

from .models import Usuario, Acesso
from fuzzywuzzy import fuzz
from .services import vincular_por_matricula

from django.core.cache import cache

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 3})
def processar_xls(self, caminho_arquivo):

    self.update_state(state="STARTED")
    print("PROCESSANDO:", caminho_arquivo)

    df = pd.read_excel(caminho_arquivo)

    headers = { #signals
        "X-Api-Key": "pbkdf2_sha256$1200000$aonByYw2GbwuyDvrGd1z9w4x5BO477iAMn69G1gs3W1C3n1ZmLwxHpBZoKFIIQV0=",
        "Authorization": "Api-Key xb8vL1sU.wnTtzS31MbyyKeRICGTxTfvHKuxTSBt0",
    }

    profiles = cache.get("profiles")
    users = cache.get("users")

    if not profiles or not users:
        print("Buscando da API...")

        profiles = requests.get(
            "http://localhost:8000/api/users/user-profile/",
            headers=headers,
            timeout=10
        ).json()

        users = requests.get(
            "http://localhost:8000/api/users/user/",
            headers=headers,
            timeout=10
        ).json()

        cache.set("profiles", profiles, timeout=600)
        cache.set("users", users, timeout=600)

    print("Profiles carregados:", len(profiles))
    print("Users carregados:", len(users))

    for _, row in df.iterrows():
        matricula = str(row.get("MATRICULA", "")).strip()

        if "NOME_ALUNO" in df.columns:
            nome_usuario = row.get("NOME_ALUNO", "")
            categoria = matricula[:3]
        elif "NOME_FUNCIONARIO" in df.columns:
            nome_usuario = row.get("NOME_FUNCIONARIO", "")
            categoria = "FUNCIONARIO"
        else:
            nome_usuario = "Desconhecido"

        usuario, _ = Usuario.objects.get_or_create(
            matricula=matricula,
            defaults={
                "nome_usuario": nome_usuario,
                "categoriaUsuario": categoria,
            }
        )


        data = timezone.make_aware(pd.to_datetime(row.get("DATA")))

        Acesso.objects.get_or_create(
            usuario=usuario,
            data_acesso=data,
            desc_evento=row.get("DESC_EVENTO", ""),
            desc_area=row.get("DESC_AREA", ""),
            ent_sai=row.get("ENT_SAI", ""),
            defaults={
                "desc_leitor": row.get("DESC_LEITOR", "")
            }
        )

        if usuario.user_auth is None:
            tentar_vincular_user_auth.delay(usuario.id)

    print("PROCESSAMENTO FINALIZADO")


@shared_task(bind=True)
def tentar_vincular_user_auth(self, usuario_id):
    self.update_state(state="STARTED")

    profiles = cache.get("profiles")
    users = cache.get("users")

    if not profiles or not users:
        print("Cache vazio!")
        return False

    usuario = Usuario.objects.filter(
        id=usuario_id,
        user_auth__isnull=True
    ).first()

    if not usuario:
        return False

    vinculou = vincular_por_matricula(usuario, profiles)

    if not vinculou:
        tentar_vincular_por_nome.delay(usuario.id)

    return vinculou

@shared_task(bind=True)
def tentar_vincular_por_nome(self, usuario_id):
    self.update_state(state="STARTED")

    users = cache.get("users")

    if not users:
        print("Cache users vazio!")
        return False

    usuario = Usuario.objects.filter(
        id=usuario_id,
        user_auth__isnull=True
    ).first()

    if not usuario or not usuario.nome_usuario:
        return False

    nome_usuario = usuario.nome_usuario.lower().strip()
    melhor = None
    score_max = 0

    for user in users:
        nome_db = (user.get("full_name") or "").lower().strip()
        if not nome_db:
            continue

        score = fuzz.token_sort_ratio(nome_usuario, nome_db)
        if score > score_max:
            score_max = score
            melhor = user

    if melhor and score_max >= 80:
        usuario.user_auth = melhor.get("id")
        usuario.save(update_fields=["user_auth"])
        return True

    return False