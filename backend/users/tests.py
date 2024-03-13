import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

DEFAULT_NUMBER_OF_USERS = 0
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestAPIRegistrationAndAuthenticationUser(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = APIClient()
        cls.test_user_data = {
            "email": "user@mail.ru",
            "password": "qwertyqwerty123",
        }
        cls.response_registration = cls.client.post(
            "/api/v2/users/", cls.test_user_data
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_registration(self):
        response = self.response_registration
        user = User.objects.first()
        user_data = [user.id, user.email]
        user_count = User.objects.count()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(user_data, [*response.data.values()])
        self.assertEqual(user_count, DEFAULT_NUMBER_OF_USERS + 1)

    def test_authentication(self):
        response_registration = self.response_registration
        response_token_login = self.client.post(
            "/api/v2/auth/token/login/", self.test_user_data
        )
        response_auth = self.client.get(
            "/api/v2/users/me/",
            HTTP_AUTHORIZATION=f'Token {response_token_login.data["auth_token"]}',
        )
        self.assertEqual(
            response_registration.data["id"],
            response_auth.data["id"],
        )
        self.assertEqual(
            response_registration.data["email"],
            response_auth.data["email"],
        )