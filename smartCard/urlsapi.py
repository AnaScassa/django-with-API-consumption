from django.urls import include, path
from rest_framework import routers
from smartCard.api import UserViewSet
from smartCard.views import UserViewSetApi
from smartCard.api import AcessoViewSet, GroupViewSet, UsuarioViewSet


router = routers.DefaultRouter()
router.register(r"userAuth", UserViewSetApi) 
router.register(r"groups", GroupViewSet)
router.register(r"acessos", AcessoViewSet)
router.register(r'usuarios', UsuarioViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path("userAuth2/", UserViewSetApi.as_view({'get': 'list'})),
]


# criar endpoint do upload, acessar o endpoint do users dentro da função "tentar_vincular_user_auth"
# alterar o algoritimo para fazer a busca com o thefuzz
# lembrar de usar o frontend do projeto "docker"
# verificar endpoints acessados pelo frontend 