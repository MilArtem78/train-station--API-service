from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from train_station.models import Ticket
from .create_sample_models import (
    sample_route,
    sample_station,
    sample_train_type,
    sample_train,
    sample_crew,
    sample_trip,
    sample_order,
)


class ModelsTest(TestCase):
    def test_station_str(self):
        station = sample_station(name="Test_1")
        self.assertEqual(str(station), station.name)

    def test_station_name_uniqueness(self):
        sample_station(name="Test_1")
        with self.assertRaises(IntegrityError):
            sample_station(name="Test_1")

    def test_route_str(self):
        station1 = sample_station(name="Test_1")
        station2 = sample_station(name="Test_2")
        route = sample_route(station1, station2)

        self.assertEqual(str(route), f"{station1} - {station2}")

    def test_route_source_destination_are_not_same(self):
        station1 = sample_station(name="Test_1")
        with self.assertRaises(ValidationError):
            sample_route(station1, station1)

    def test_route_source_destination_uniqueness(self):
        station1 = sample_station(name="Test_1")
        station2 = sample_station(name="Test_2")
        sample_route(station1, station2)

        with self.assertRaises(ValidationError):
            sample_route(station1, station2)

    def test_train_type_str(self):
        train_type = sample_train_type(name="Test_1")
        self.assertEqual(str(train_type), train_type.name)

    def test_train_type_name_uniqueness(self):
        sample_train_type(name="Test_1")
        with self.assertRaises(IntegrityError):
            sample_train_type(name="Test_1")

    def test_train_str(self):
        train = sample_train_type(name="Test_1")
        self.assertEqual(str(train), train.name)

    def test_train_name_uniqueness(self):
        sample_train(name="Test_1")
        with self.assertRaises(IntegrityError):
            sample_train(name="Test_1")

    def test_train_capacity_property(self):
        train = sample_train(
            name="Test_1",
            cargo_num=5,
            places_in_cargo=15,
        )

        self.assertEqual(train.capacity, 75)

    def test_crew_str(self):
        crew_member = sample_crew(
            first_name="first_name_test",
            last_name="last_name_test"
        )
        expect = f"{crew_member.first_name} {crew_member.last_name}"

        self.assertEqual(str(crew_member), expect)

    def test_crew_full_name_capacity(self):
        crew_member = sample_crew(
            first_name="first_name_test",
            last_name="last_name_test"
        )
        expect = f"{crew_member.first_name} {crew_member.last_name}"

        self.assertEqual(crew_member.full_name, expect)

    def test_trip_str(self):
        trip = sample_trip(name="Test_1")
        expect = (
            f"Trip {trip.route.source} - {trip.route.destination}, "
            f" train — {trip.train.name}, "
            f"[{trip.departure_time} - {trip.arrival_time}]"
        )

        self.assertEqual(str(trip), expect)

    def test_order_str(self):
        user = get_user_model().objects.create(
            email="test@test.test", password="test_password"
        )
        order = sample_order(user=user)

        self.assertEqual(str(order), f"{order.created_at}")

    def test_ticket_str(self):
        user = get_user_model().objects.create(
            email="test@test.test", password="test_password"
        )
        trip = sample_trip(name="Test_1")
        ticket = Ticket.objects.create(
            cargo=1, seat=1, trip=trip, order=sample_order(user=user)
        )

        expect = f"{ticket.trip} (cargo: {ticket.cargo}, seat: {ticket.seat})"

        self.assertEqual(str(ticket), expect)

    def test_validate_ticket_method_where_invalid_cargo(self):
        train = sample_train(
            name="Test_1", cargo_num=8, places_in_cargo=8,
        )
        trip = sample_trip(train=train, name="Test_2")
        user = get_user_model().objects.create(
            email="test@test.test", password="test_password"
        )

        with self.assertRaises(ValidationError):
            Ticket.objects.create(
                cargo=9, seat=6, trip=trip, order=sample_order(user=user)
            )

    def test_validate_ticket_method_where_invalid_places_in_cargo(self):
        train = sample_train(
            name="Test_1", cargo_num=8, places_in_cargo=8,
        )
        trip = sample_trip(train=train, name="Test_2")
        user = get_user_model().objects.create(
            email="test@test.test", password="test_password"
        )

        with self.assertRaises(ValidationError):
            Ticket.objects.create(
                cargo=5, seat=15, trip=trip, order=sample_order(user=user)
            )

    def test_ticket_cargo_seat_trip_field_uniqueness(self):
        train = sample_train(
            name="Test_1", cargo_num=5, places_in_cargo=5,
        )
        trip = sample_trip(train=train, name="Test_2")
        user = get_user_model().objects.create(
            email="test@test.test", password="test_password"
        )
        Ticket.objects.create(
            cargo=3, seat=3, trip=trip, order=sample_order(user=user)
        )

        with self.assertRaises(ValidationError):
            Ticket.objects.create(
                cargo=3, seat=3, trip=trip, order=sample_order(user=user)
            )