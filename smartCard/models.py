from django.db import models
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

        matricula = self.matricula.strip()

        for profile in UserProfile.objects.select_related("user"):
            if profile.academic_id and profile.academic_id.strip() == matricula:
                self.user_auth = profile.user
                return

        if not self.nome_usuario:
            return

        nome_usuario = self.nome_usuario.strip().lower()

        melhor_match = None
        melhor_score = 0

        for user in User.objects.all():
            nome_user = f"{user.first_name} {user.last_name}".strip().lower()

            if not nome_user:
                continue

            score = fuzz.token_sort_ratio(nome_usuario, nome_user)

            if score > melhor_score:
                melhor_score = score
                melhor_match = user

        if melhor_match and melhor_score >= 80:
            self.user_auth = melhor_match

    def save(self, *args, **kwargs):
        if not self.user_auth:
            self.tentar_vincular_user_auth()

        super().save(*args, **kwargs)


class Acesso(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        to_field='matricula',
        related_name='acessos',
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
