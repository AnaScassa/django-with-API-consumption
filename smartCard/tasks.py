from celery import shared_task
import pandas as pd
import requests
from .models import Usuario, Acesso
from .services import tentar_vincular_user_auth
from fuzzywuzzy import fuzz

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 3})
def processar_xls(self, caminho_arquivo):
    print("PROCESSANDO:", caminho_arquivo)

    df = pd.read_excel(caminho_arquivo)

    headers = {
        "X-Api-Key": "pbkdf2_sha256$1200000$aonByYw2GbwuyDvrGd1z9w4x5BO477iAMn69G1gs3W1C3n1ZmLwxHpBZoKFIIQV0=",        
        "Authorization": "Api-Key xb8vL1sU.wnTtzS31MbyyKeRICGTxTfvHKuxTSBt0",
    }

    users = requests.get(
        "http://localhost:8000/api/users/user/",
        headers=headers,
        timeout=10
    ).json()

    profiles = requests.get(
        "http://localhost:8000/api/users/user-profile/",
        headers=headers,
        timeout=10
    ).json()

    for _, row in df.iterrows():
        matricula = str(row.get("MATRICULA", "")).strip()
        categoria = matricula[:3]

        usuario, _ = Usuario.objects.get_or_create(
            matricula=matricula,
            defaults={
                "nome_usuario": row.get("NOME_ALUNO", "Desconhecido"),
                "categoriaUsuario": categoria
            }
        )

        data = row.get("DATA")
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

        if usuario.user_auth == None:
            tentar_vincular_user_auth(usuario, users, profiles)
    users = requests.get(
        "http://localhost:8000/api/users/user/",
        headers=headers,
        timeout=10
    ).json()

    print("PROCESSAMENTO FINALIZADO")

@shared_task
def tentar_vincular_por_nome(usuario_id, users):
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