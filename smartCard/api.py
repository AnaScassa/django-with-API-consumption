from django.contrib.auth.models import Group
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework.authentication import SessionAuthentication
from smartcard.models import User, Acesso, Usuario
from smartcard.serializers import (
    GroupSerializer,
    UserSerializer,
    AcessoSerializer,
    UsuarioSerializer,
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated | HasAPIKey]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated | HasAPIKey]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

class AcessoViewSet(viewsets.ModelViewSet):
    queryset = Acesso.objects.all() 
    serializer_class = AcessoSerializer
    permission_classes = [IsAuthenticated | HasAPIKey]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

class UsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Usuario.objects.all().order_by("nome_usuario")
    serializer_class = UsuarioSerializer 
    permission_classes = [IsAuthenticated | HasAPIKey]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

    def get_queryset(self):
        return super().get_queryset()
