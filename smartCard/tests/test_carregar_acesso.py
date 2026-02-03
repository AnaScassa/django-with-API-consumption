from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()

class CarregarAcessoTest(APITestCase):

    def test_sem_autenticacao_retorna_401(self):
        response = self.client.post("/api/acesso/upload-xls/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_extensao_invalida_sem_auth_retorna_401(self):
        arquivo = SimpleUploadedFile(
            "teste.txt",
            b"arquivo invalido",
            content_type="text/plain"
        )
        response = self.client.post(
            "/api/acesso/upload-xls/",
            {"file": arquivo},
            format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_superuser_consegue_acessar_endpoint(self):
        user = User.objects.create_superuser(
            username="anacha",
            email="ana@test.com",
            password="123"
        )
        token = RefreshToken.for_user(user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {token.access_token}'
        )
        response = self.client.post("/api/acesso/upload-xls/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

   
