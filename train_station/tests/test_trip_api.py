from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.db.models import Count, F

from rest_framework.test import APIClient
from rest_framework import status

from train_station.serializers import (
    TripSerializer,
    TripListSerializer,
    TripDetailSerializer,
)
from .create_sample_models import (
    sample_trip,
    sample_train,
    sample_route,
    sample_station,
    sample_crew,
    detail_url,
)
from train_station.models import Trip

TRIP_URL = reverse("train_station:trip-list")


def set_available_tickets_field():
    """Set available_tickets field in trip instances
    so we could compare data from trip view that has
    already calculated field available_tickets"""
    trips = Trip.objects.annotate(tickets_available=(
            F("train__cargo_num") * F("train__places_in_cargo")
            - Count("tickets")
    ))
    return trips


class UnauthenticatedTripApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_get_method_auth_required(self):
        response = self.client.get(TRIP_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_method_auth_required(self):
        response = self.client.post(TRIP_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_trip_detail_auth_required(self):
        trip = sample_trip(name="Test_Trip1")
        response = self.client.get(detail_url("trip", trip.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_method_auth_required(self):
        trip = sample_trip(name="Test_Trip1")
        response = self.client.patch(detail_url("trip", trip.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_method_auth_required(self):
        trip = sample_trip(name="Test_Trip1")
        response = self.client.put(detail_url("trip", trip.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_method_auth_required(self):
        trip = sample_trip(name="Test_Trip1")
        response = self.client.delete(detail_url("trip", trip.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTripApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="test_password"
        )
        self.client.force_authenticate(self.user)

    def test_trip_list_has_tickets_available_field(self):
        sample_trip(name="Test_Trip1")

        response = self.client.get(TRIP_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tickets_available", response.data[0].keys())

    def test_trip_detail_has_taken_places_field(self):
        trip = sample_trip(name="Test_Trip1")

        response = self.client.get(detail_url("trip", trip.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("taken_places", response.data)

    def test_list_trip(self):
        sample_trip(name="Test_Trip1")
        sample_trip(name="Test_Trip2")

        response = self.client.get(TRIP_URL)

        trips = set_available_tickets_field()
        serializers = TripListSerializer(trips, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializers.data)

    def test_trip_detail_page(self):
        trip = sample_trip(name="Test_Trip1")

        response = self.client.get(detail_url("trip", trip.id))

        trip = Trip.objects.get(id=trip.id)
        serializers = TripDetailSerializer(trip)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializers.data)

    def test_filter_trip_list_by_route(self):
        station1 = sample_station("Test1")
        station2 = sample_station("Test2")
        route1 = sample_route(station1, station2)
        route2 = sample_route(station2, station1)
        trip1 = sample_trip(name="Test_Trip1")
        trip2 = sample_trip(name="Test_Trip2")
        trip3 = sample_trip(name="Test_Trip3")

        trip1.route = route1
        trip2.route = route2

        trip1.save()
        trip2.save()

        response = self.client.get(
            TRIP_URL, {"route": "Test1"}
        )
        trips = set_available_tickets_field()
        serializer1 = TripListSerializer(trips.get(id=trip1.id))
        serializer2 = TripListSerializer(trips.get(id=trip2.id))
        serializer3 = TripListSerializer(trips.get(id=trip3.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)
        self.assertNotIn(serializer3.data, response.data)

    def test_create_trip_forbidden(self):
        response = self.client.post(TRIP_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_train_api_has_only_get_and_post_methods(self):
        response = self.client.post(TRIP_URL)
        allowed_methods = response.headers["Allow"]
        forbidden_methods = ["PATCH", "PUT", "DELETE"]

        self.assertIn("GET", allowed_methods)
        self.assertIn("POST", allowed_methods)
        for method in forbidden_methods:
            self.assertNotIn(method, allowed_methods)


class AdminTripApi(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.admin = get_user_model().objects.create_superuser(
            email="test@test.test", password="test_password"
        )
        self.client.force_authenticate(self.admin)

    def test_admin_trip_can_make_get_detail(self):
        trip = sample_trip(name="Test_Trip1")
        response = self.client.get(detail_url("trip", trip.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_create_trip(self):
        route = sample_route(
            sample_station("Test1"),
            sample_station("Test2")
        )
        crew = sample_crew(
            first_name="Test_first_name", last_name="Test_last_name"
        )
        data = {
            "crew": [crew.id],
            "route": route.id,
            "train": sample_train("Test_1").id,
            "departure_time": datetime.today(),
            "arrival_time": datetime.today() + timedelta(days=2),
        }

        response = self.client.post(TRIP_URL, data)

        trip = Trip.objects.get(
            train_id=data["train"]
        )
        serializer = TripSerializer(trip)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, serializer.data)

    def test_admin_trip_can_make_put_request(self):
        trip = sample_trip(name="Test_Trip1")
        route = sample_route(
            sample_station("Test1"),
            sample_station("Test2")
        )
        crew = sample_crew(
            first_name="Test_first_name", last_name="Test_last_name"
        )
        data = {
            "crew": [crew.id],
            "route": route.id,
            "train": sample_train("Test_1").id,
            "departure_time": datetime.today(),
            "arrival_time": datetime.today(),
        }

        response = self.client.put(
            detail_url("trip", trip.id),
            data
        )

        trip = Trip.objects.get(id=trip.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["route"], trip.route.id,
        )
        self.assertEqual(
            response.data["crew"][0], crew.id,
        )
        self.assertEqual(
            response.data["train"], trip.train.id,
        )

    def test_admin_trip_can_make_patch_request(self):
        trip = sample_trip(name="Test_Trip1")
        route = sample_route(
            sample_station("Test1"),
            sample_station("Test2")
        )
        data = {
            "crew": [],
            "route": route.id,
            "arrival_time": datetime.today() + timedelta(days=2),
        }

        response = self.client.patch(
            detail_url("trip", trip.id),
            data
        )
        trip = Trip.objects.get(id=trip.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["crew"], []
        )
        self.assertEqual(
            response.data["route"], trip.route.id,
        )

    def test_admin_can_delete_trip(self):
        trip = sample_trip(name="Test_Trip1")

        res = self.client.delete(
            detail_url("trip", trip.id)
        )

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Trip.DoesNotExist):
            Trip.objects.get(id=trip.id)
