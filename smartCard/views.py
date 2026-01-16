from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone

import pandas as pd

from smartCard.models import Acesso, Usuario
from users.models import User
from .serializers import UserApiSerializer, UsuarioSerializer
from rest_framework_api_key.permissions import HasAPIKey

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
    print("USER:", request.user)
    print("AUTH:", request.user.is_authenticated)

    if 'file' not in request.FILES:
        return Response(
            {"erro": "Nenhum arquivo enviado. Use 'file' no form-data."},
            status=status.HTTP_400_BAD_REQUEST
        )

    arquivo = request.FILES['file']

    if not arquivo.name.endswith(".xls"):
        return Response(
            {"erro": "Apenas arquivos .xls são permitidos."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        df = pd.read_excel(arquivo, engine="xlrd")
    except Exception as e:
        return Response(
            {"erro": f"Erro ao processar planilha: {e}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    novos = 0
    duplicados = 0

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
        if data and timezone.is_naive(data):
            data = timezone.make_aware(data)

        _, created = Acesso.objects.get_or_create(
            usuario=usuario,
            data_acesso=data,
            desc_evento=row.get("DESC_EVENTO", ""),
            desc_area=row.get("DESC_AREA", ""),
            desc_leitor=row.get("DESC_LEITOR", ""),
            ent_sai=row.get("ENT_SAI", "")
        )

        if created:
            novos += 1
        else:
            duplicados += 1

    return Response(
        {
            "novos_registros": novos,
            "registros_duplicados": duplicados,
            "total_linhas": len(df)
        },
        status=status.HTTP_201_CREATED
    )
