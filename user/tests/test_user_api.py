from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from user.models import User


class UserTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="test_password"
        )

    def test_registration(self):
        url = reverse("user:create")
        payload = {
            "email": "test_1@test.test",
            "password": "test_password_1",
        }
        response = self.client.post(url, payload, format="json")
        user = User.objects.get(id=response.data["id"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data.get("id"))
        self.assertEqual(payload["email"], getattr(user, "email"))

    def test_token_obtaining(self):
        url = reverse("user:token_obtain_pair")
        data = {
            "email": "test@test.test",
            "password": "test_password",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get("access"))
        self.assertIsNotNone(response.data.get("refresh"))

    def test_token_refresh(self):
        url = reverse("user:token_refresh")
        obtain_token_url = reverse("user:token_obtain_pair")
        login_data = {
            "email": "test@test.test",
            "password": "test_password",
        }
        response_obtain_token = self.client.post(
            obtain_token_url, login_data, format="json"
        )
        refresh_token = response_obtain_token.data.get("refresh")

        response = self.client.post(url, {"refresh": refresh_token}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get("access"))

    def test_token_verification(self):
        url = reverse("user:token_verify")

        obtain_token_url = reverse("user:token_obtain_pair")
        login_data = {
            "email": "test@test.test",
            "password": "test_password",
        }
        response_obtain_token = self.client.post(
            obtain_token_url, login_data, format="json"
        )
        access_token = response_obtain_token.data.get("access")
        response = self.client.post(url, {"token": access_token}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manage_user_data(self):
        url = reverse("user:manage")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.email, response.data.get("email"))