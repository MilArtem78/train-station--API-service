from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from train_station.serializers import (
    TrainListSerializer,
    TrainDetailSerializer,
    TrainSerializer
)
from .create_sample_models import sample_train, detail_url, sample_train_type
from train_station.models import Train

TRAIN_URL = reverse("train_station:train-list")


class UnauthenticatedTrainApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(TRAIN_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTrainApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="test_password"
        )
        self.client.force_authenticate(self.user)

    def test_list_train(self):
        sample_train(name="Test_Train_1")
        sample_train(name="Test_Train_2")

        response = self.client.get(TRAIN_URL)

        trains = Train.objects.all()
        serializers = TrainListSerializer(trains, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializers.data)

    def test_filter_trains_by_train_types(self):
        train_type_1 = sample_train_type(name="Test_1")
        train_type_2 = sample_train_type(name="Test_2")
        train_type_3 = sample_train_type(name="Test_3")
        train_1 = sample_train(name="Test_Train1", train_type=train_type_1)
        train_2 = sample_train(name="Test_Train2", train_type=train_type_2)
        train_3 = sample_train(name="Test_Train3", train_type=train_type_3)
        response = self.client.get(
            TRAIN_URL,
            {"train_type": f"{train_type_1.id},{train_type_2.id}"}
        )

        serializer_1 = TrainListSerializer(train_1)
        serializer_2 = TrainListSerializer(train_2)
        serializer_3 = TrainListSerializer(train_3)

        self.assertIn(serializer_1.data, response.data)
        self.assertIn(serializer_2.data, response.data)
        self.assertNotIn(serializer_3.data, response.data)

    def test_filter_trains_by_names(self):
        train_1 = sample_train(name="Test_Train1")
        train_2 = sample_train(name="Test_Train2")
        train_3 = sample_train(name="Test_3")
        response = self.client.get(
            TRAIN_URL,
            {"name": "train"}
        )

        serializer_1 = TrainListSerializer(train_1)
        serializer_2 = TrainListSerializer(train_2)
        serializer_3 = TrainListSerializer(train_3)

        self.assertIn(serializer_1.data, response.data)
        self.assertIn(serializer_2.data, response.data)
        self.assertNotIn(serializer_3.data, response.data)

    def test_retrieve_train_detail(self):
        train = sample_train(name="Test_Train1")

        url = detail_url("train", train.id)
        response = self.client.get(url)
        serializer = TrainDetailSerializer(train)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_train_forbidden(self):
        response = self.client.post(TRAIN_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_train_api_has_only_get_and_post_methods(self):
        response = self.client.post(TRAIN_URL)
        allowed_methods = response.headers["Allow"]
        forbidden_methods = ["PATCH", "PUT", "DELETE"]

        self.assertIn("GET", allowed_methods)
        self.assertIn("POST", allowed_methods)
        for method in forbidden_methods:
            self.assertNotIn(method, allowed_methods)


class AdminTrainApi(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.admin = get_user_model().objects.create_user(
            email="test@test.test", password="test_password", is_staff=True
        )
        self.client.force_authenticate(self.admin)

    def test_admin_can_make_get_request(self):
        sample_train(name="Test_Train_1")
        sample_train(name="Test_Train_2")

        response = self.client.get(TRAIN_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_create_train(self):
        payload = {
            "name": "Test_Train2",
            "cargo_num": 8,
            "places_in_cargo": 10,
            "train_type": sample_train_type(name="Test_1").id,
        }
        response = self.client.post(TRAIN_URL, payload)
        train = Train.objects.get(name=response.data["name"])
        serializer = TrainSerializer(train)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, serializer.data)

    def test_delete_train_not_allowed(self):
        train = sample_train(name="Test_Train1")
        url = detail_url("train", train.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
