from django.contrib.auth.models import Group
from smartCard.models import User
from rest_framework import permissions, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_api_key.permissions import HasAPIKey

from smartCard.models import Acesso, Usuario
from smartCard.serializers import GroupSerializer, UserSerializer, AcessoSerializer, UsuarioSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permissions_classes = [IsAuthenticated | HasAPIKey]

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupSerializer
    permissions_classes = [IsAuthenticated | HasAPIKey]

class AcessoViewSet(viewsets.ModelViewSet):
    queryset = Acesso.objects.all() 
    serializer_class = AcessoSerializer
    permissions_classes = [IsAuthenticated | HasAPIKey]
    authentication_classes = [JWTAuthentication]




class UsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Usuario.objects.all().order_by("nome_usuario")
    serializer_class = UsuarioSerializer 
    permissions_classes = [ IsAuthenticated | HasAPIKey ]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return super().get_queryset()
