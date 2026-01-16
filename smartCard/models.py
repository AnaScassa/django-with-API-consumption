from django.db import models
import requests
from thefuzz import fuzz
from django.db import models
from thefuzz import fuzz
from users.models import User, UserProfile

class Usuario(models.Model):
    matricula = models.CharField(max_length=20, unique=True)
    nome_usuario = models.CharField(max_length=100)
    categoriaUsuario = models.CharField(max_length=50, blank=True, null=True)

    user_auth = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.nome_usuario} ({self.matricula})"

    def tentar_vincular_user_auth(self):

        if self.user_auth:
            return

        matricula = str(self.matricula).strip()

        url = "http://localhost:8000/api/acesso/usuarios"
        headers = {
            "X-Api-Key": "pbkdf2_sha256$1200000$aonByYw2GbwuyDvrGd1z9w$4x5BO477iAMn69G1gs3W1C3n1ZmLwxHpBZoKFII+QV0=",
            "Authorization": "Api-Key t37FhVxu.ZLsNAnOIlAwhFatVRVNWnNNEzX2UPRK1",

        }

        try:
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            profiles = response.json()  
        except requests.RequestException:
            return

        for profile in profiles:
            academic_id = profile.get("academic_id")

            if academic_id and academic_id.strip() == matricula:
                user_id = profile.get("user")

                if not user_id:
                    return

                try:
                    self.user_auth = User.objects.get(id=user_id)
                    return
                except User.DoesNotExist:
                    return

        if not self.nome_usuario:
            return

        nome_usuario = self.nome_usuario.strip().lower()

        melhor_match = None
        melhor_score = 0

        for profile in profiles:
            nome_api = profile.get("full_name", "").strip().lower()

            if not nome_api:
                continue

            score = fuzz.token_sort_ratio(nome_usuario, nome_api)

            if score > melhor_score:
                melhor_score = score
                melhor_match = profile

        if melhor_match and melhor_score >= 80:
            user_id = melhor_match.get("user")

            if not user_id:
                return

            try:
                self.user_auth = User.objects.get(id=user_id)
            except User.DoesNotExist:
                pass

    def save(self, *args, **kwargs):
        if not self.user_auth:
            self.tentar_vincular_user_auth()

        super().save(*args, **kwargs)

class Acesso(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        to_field = 'matricula',
        related_name ='acessos',
        on_delete=models.CASCADE
    ) 
    data_acesso = models.DateTimeField() 
    desc_evento = models.CharField(max_length=100) 
    desc_area = models.CharField(max_length=100) 
    desc_leitor = models.CharField(max_length=100) 
    ent_sai = models.CharField(max_length=10) 

    class Meta: 
        unique_together = ('usuario', 'data_acesso', 'desc_evento', 'desc_area', 'ent_sai') 

    def __str__(self): 
        return f"Acesso de {self.usuario.nome_usuario} em {self.data_acesso}" 
