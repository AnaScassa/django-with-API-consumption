from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile


class CarregarAcessoTest(APITestCase):

    def test_sem_autenticacao_retorna_401(self):
        response = self.client.post("/api/acesso/upload-xls/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_sem_arquivo_sem_auth_retorna_401(self):
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
