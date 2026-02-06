from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .tasks import processar_xls
from .services import salvar_arquivo_temporario
from django.urls import reverse

from smartcard.models import Acesso, Usuario
from users.models import User
from .serializers import UserApiSerializer
from rest_framework_api_key.permissions import HasAPIKey
from .models import Usuario

class UserViewSetApi(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserApiSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def lista_acessos(request):
    acessos = Acesso.objects.values(
        'id',
        'usuario_id',
        'data_acesso',
        'desc_evento',
        'desc_area',
        'desc_leitor',
        'ent_sai'
    )
    return Response(list(acessos), status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([HasAPIKey])
def lista_usuarios(request):
    usuarios = Usuario.objects.values(
        'id',
        'nome_usuario'
    )
    return Response(list(usuarios), status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated | HasAPIKey])
def carregar_acesso(request):
    arquivo = request.FILES.get("file")

    if not arquivo:
        return Response(
            {"erro": "Nenhum arquivo enviado."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not arquivo.name.endswith(".xls"):
        return Response(
            {"erro": "Apenas arquivos .xls são permitidos."},
            status=status.HTTP_400_BAD_REQUEST
        )

    caminho = salvar_arquivo_temporario(arquivo)

    task = processar_xls.delay(caminho)

    response = Response(
        {
            "mensagem": "Arquivo enviado para processamento",
            "task_id": task.id,
        },
        status=status.HTTP_202_ACCEPTED
    )

    response["Location"] = reverse("upload_xls")
    return response
