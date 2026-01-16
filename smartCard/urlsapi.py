from django.urls import include, path
from rest_framework import routers
from smartCard.views import UserViewSetApi, carregar_acesso, lista_usuarios
from smartCard.api import AcessoViewSet, GroupViewSet, UsuarioViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = routers.DefaultRouter()
router.register(r"userAuth", UserViewSetApi)
router.register(r"groups", GroupViewSet)
router.register(r"acessos", AcessoViewSet)
router.register(r"usuarios", UsuarioViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path("upload-xls/", carregar_acesso),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("lista-usuarios/", lista_usuarios, name="lista_usuarios"),
]
