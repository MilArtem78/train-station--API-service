from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from train_station.serializers import (
    RouteListSerializer
)
from .create_sample_models import sample_route, sample_station, detail_url
from train_station.models import Route

ROUTE_URL = reverse("train_station:route-list")


class UnauthenticatedRouteApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(ROUTE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="test_password"
        )
        self.client.force_authenticate(self.user)

    def test_list_route(self):
        sample_route(sample_station(name="Test1"), sample_station(name="Test2"))
        sample_route(sample_station(name="Test3"), sample_station(name="Test4"))

        response = self.client.get(ROUTE_URL)

        routes = Route.objects.all()
        serializers = RouteListSerializer(routes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializers.data)

    def test_create_route_forbidden(self):
        response = self.client.post(ROUTE_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_route_api_has_only_get_and_post_methods(self):
        response = self.client.post(ROUTE_URL)
        allowed_methods = response.headers["Allow"]
        forbidden_methods = ["PATCH", "PUT", "DELETE"]

        self.assertIn("GET", allowed_methods)
        self.assertIn("POST", allowed_methods)
        for method in forbidden_methods:
            self.assertNotIn(method, allowed_methods)


class AdminRouteApi(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.admin = get_user_model().objects.create_user(
            email="test@test.test", password="test_password", is_staff=True
        )
        self.client.force_authenticate(self.admin)
        self.route = sample_route(sample_station(name="Test1"), sample_station(name="Test2"))

    def test_admin_can_create_route(self):
        station1 = sample_station(name="Test_1")
        station2 = sample_station(name="Test_2")
        payload = {
            "source": station1.id,
            "destination": station2.id,
            "distance": 50
        }
        response = self.client.post(ROUTE_URL, payload)
        route = Route.objects.get(id=response.data["id"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(station1, getattr(route, "source"))
        self.assertEqual(station2, getattr(route, "destination"))
        self.assertEqual(payload["distance"], getattr(route, "distance"))

    def test_delete_route_not_allowed(self):
        url = detail_url("route", self.route.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_route_not_allowed(self):
        url = detail_url("route", self.route.id)
        updated = {
            "distance": 5
        }

        response = self.client.put(url, data=updated)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
