from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from train_station.serializers import (
    TrainTypeSerializer
)
from .create_sample_models import sample_train_type
from train_station.models import TrainType

TRAIN_TYPE_URL = reverse("train_station:traintype-list")


class UnauthenticatedTraintypeApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(TRAIN_TYPE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTraintypeApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="test_password"
        )
        self.client.force_authenticate(self.user)

    def test_list_traintype(self):
        sample_train_type(name="Test_1")
        sample_train_type(name="Test_2")

        response = self.client.get(TRAIN_TYPE_URL)

        train_types = TrainType.objects.all()
        serializers = TrainTypeSerializer(train_types, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializers.data)

    def test_create_traintype_forbidden(self):
        response = self.client.post(TRAIN_TYPE_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_traintype_api_has_only_get_and_post_methods(self):
        response = self.client.post(TRAIN_TYPE_URL)
        allowed_methods = response.headers["Allow"]
        forbidden_methods = ["PATCH", "PUT", "DELETE"]

        self.assertIn("GET", allowed_methods)
        self.assertIn("POST", allowed_methods)
        for method in forbidden_methods:
            self.assertNotIn(method, allowed_methods)


class AdminTraintypeApi(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.admin = get_user_model().objects.create_user(
            email="test@test.test", password="test_password", is_staff=True
        )
        self.client.force_authenticate(self.admin)

    def test_admin_can_create_traintype(self):
        payload = {
            "name": "Test"
        }
        response = self.client.post(TRAIN_TYPE_URL, payload)
        traintype = TrainType.objects.get(id=response.data["id"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(payload[key], getattr(traintype, key))
