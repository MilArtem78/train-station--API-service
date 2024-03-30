from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from train_station.serializers import (
    StationSerializer
)
from .create_sample_models import sample_station
from train_station.models import Station

STATION_URL = reverse("train_station:station-list")


class UnauthenticatedStationApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(STATION_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedStationApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="test_password"
        )
        self.client.force_authenticate(self.user)

    def test_list_station(self):
        sample_station(name="Test_1")
        sample_station(name="Test_2")

        response = self.client.get(STATION_URL)

        stations = Station.objects.all()
        serializers = StationSerializer(stations, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializers.data)

    def test_create_station_forbidden(self):
        response = self.client.post(STATION_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_station_api_has_only_get_and_post_methods(self):
        response = self.client.post(STATION_URL)
        allowed_methods = response.headers["Allow"]
        forbidden_methods = ["PATCH", "PUT", "DELETE"]

        self.assertIn("GET", allowed_methods)
        self.assertIn("POST", allowed_methods)
        for method in forbidden_methods:
            self.assertNotIn(method, allowed_methods)


class AdminStationApi(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.admin = get_user_model().objects.create_user(
            email="test@test.test", password="test_password", is_staff=True
        )
        self.client.force_authenticate(self.admin)

    def test_admin_can_create_station(self):
        payload = {
            "name": "Test",
            "longitude": 50,
            "latitude": 50,
        }
        response = self.client.post(STATION_URL, payload)
        station = Station.objects.get(id=response.data["id"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(payload[key], getattr(station, key))
