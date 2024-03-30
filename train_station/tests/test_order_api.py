from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from train_station.serializers import (
    OrderListSerializer,
)
from .create_sample_models import (
    sample_trip,
    sample_order,
    sample_ticket,
    sample_train
)
from train_station.models import Order

ORDER_URL = reverse("train_station:order-list")


class UnauthenticatedOrderApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_get_method_auth_required(self):
        response = self.client.get(ORDER_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedOrderApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="test_password"
        )

        self.client.force_authenticate(self.user)

    def test_orders_are_filtered_by_user(self):
        user2 = get_user_model().objects.create_user(
            email="test_1@test.test", password="test_password_1"
        )

        trip1 = sample_trip("Test_Trip1")
        trip2 = sample_trip("Test_Trip2")
        sample_ticket(user2, trip2)
        sample_ticket(self.user, trip1)

        response = self.client.get(ORDER_URL)

        user_orders = Order.objects.filter(user=self.user)
        serializer = OrderListSerializer(user_orders, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_list_order(self):
        sample_order(self.user)

        response = self.client.get(ORDER_URL)

        orders = Order.objects.all()
        serializers = OrderListSerializer(orders, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializers.data)

    def test_user_can_create_valid_order(self):
        trip = sample_trip(name="TestTrip")
        order_data = {
            "tickets": [
                {
                    "cargo": 1,
                    "seat": 1,
                    "trip": trip.id
                }
            ]
        }
        response = self.client.post(ORDER_URL, order_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_create_invalid_order_invalid_cargo_field(self):
        train = sample_train(
            name="TestTrain1", places_in_cargo=5, cargo_num=5
        )
        trip = sample_trip(name="TestTrip", train=train)
        order_data = {
            "tickets": [
                {
                    "cargo": 6,
                    "seat": 5,
                    "trip": trip.id
                }
            ]
        }
        response = self.client.post(ORDER_URL, order_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_create_invalid_order_invalid_seat_field(self):
        train = sample_train(
            name="Train1", places_in_cargo=5, cargo_num=5
        )
        trip = sample_trip(name="TestTrip", train=train)
        order_data = {
            "tickets": [
                {
                    "cargo": 5,
                    "seat": 6,
                    "trip": trip.id
                }
            ]
        }
        response = self.client.post(ORDER_URL, order_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_not_create_order_without_tickets(self):
        order_data = {
            "tickets": []
        }
        response = self.client.post(ORDER_URL, order_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
