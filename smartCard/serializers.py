from rest_framework import serializers
from smartcard.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import Group
from smartcard.models import User
from rest_framework import serializers
from smartcard.models import UserProfile
from smartcard.models import Acesso, Usuario

class UserApiSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "username",
            "email",
            "first_name",
            "last_name",
            "date_joined"
        ]

class UsuarioSerializer(serializers.HyperlinkedModelSerializer):
    acessos = serializers.SerializerMethodField()
    user_auth_id = serializers.SerializerMethodField() 
    class Meta:
        model = Usuario
        fields = [
            'url',
            'id',
            'user_auth_id',
            'matricula',
            'nome_usuario',
            'acessos',
        ]

    def get_acessos(self, obj):
        return list(
            obj.acessos.values(
                'data_acesso',
                'desc_area',
                'ent_sai'
            )
        )

    def get_user_auth_id(self, obj):
        return obj.user_auth.id if obj.user_auth else None


class AcessoSerializer(serializers.HyperlinkedModelSerializer):
    usuario = serializers.SlugRelatedField(
        slug_field='matricula',
        queryset=Usuario.objects.all()
    )

    username_auth = serializers.SerializerMethodField()
    email_auth = serializers.SerializerMethodField()
    _perfil_cache = {}

    class Meta:
        model = Acesso
        fields = [
            'url',
            'id',
            'usuario',
            'data_acesso',
            'desc_evento',
            'desc_area',
            'desc_leitor',
            'ent_sai',
            'username_auth',
            'email_auth',
        ]

    def _get_perfil(self, matricula):
        if matricula not in self._perfil_cache:
            self._perfil_cache[matricula] = (
                UserProfile.objects
                .filter(academic_id=matricula)
                .select_related('user')
                .first()
            )
        return self._perfil_cache[matricula]

    def get_username_auth(self, obj):
        perfil = self._get_perfil(obj.usuario.matricula)
        return perfil.user.username if perfil else None

    def get_email_auth(self, obj):
        perfil = self._get_perfil(obj.usuario.matricula)
        return perfil.user.email if perfil else None

class UploadAcessoSerializer(serializers.Serializer):
    arquivo = serializers.FileField()

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "groups"]

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]

