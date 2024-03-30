from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from .create_sample_models import (
    sample_station,
    sample_route,
    sample_train_type,
    sample_train,
    sample_crew,
    sample_trip,
    sample_order,
)
from train_station.admin import TripAdmin, OrderAdmin


class AdminTest(TestCase):
    def setUp(self) -> None:
        self.admin = get_user_model().objects.create_superuser(
            email="test@test.test", password="test_password"
        )
        self.client.force_login(self.admin)

    def test_admin_station_site_has_require_fields(self):
        station = sample_station(name="Test_1")
        url = reverse(
            "admin:train_station_station_changelist"
        )
        response = self.client.get(url)

        self.assertContains(response, station.name)
        self.assertContains(response, station.longitude),
        self.assertContains(response, station.latitude),

    def test_admin_station_search_by_name(self):
        station1 = sample_station(name="Test_1")
        station2 = sample_station(name="Test_2")

        url = reverse(
            "admin:train_station_station_changelist"
        )

        response = self.client.get(url, {"q": station1.name.lower()})

        changelist = response.context["cl"]
        self.assertIn(
            station1, changelist.queryset
        )
        self.assertNotIn(
            station2, changelist.queryset
        )

    def test_admin_route_site_has_require_fields(self):
        station1 = sample_station(name="Test_1")
        station2 = sample_station(name="Test_2")
        route = sample_route(station1, station2)

        url = reverse(
            "admin:train_station_route_changelist"
        )
        response = self.client.get(url)

        self.assertContains(response, route.id),
        self.assertContains(response, route.source)
        self.assertContains(response, route.destination),
        self.assertContains(response, route.distance),

    def test_admin_route_search_by_source(self):
        station1 = sample_station(name="Test_1")
        station2 = sample_station(name="Test_2")
        route1 = sample_route(station1, station2)
        route2 = sample_route(station2, station1)

        url = reverse(
            "admin:train_station_route_changelist"
        )

        response = self.client.get(url, {"q": station1.name.lower()})

        changelist = response.context["cl"]
        self.assertIn(
            route1, changelist.queryset
        )
        self.assertIn(
            route2, changelist.queryset
        )

    def test_trip_type_admin_has_require_field(self):
        train_type = sample_train_type(name="Test_1")

        url = reverse(
            "admin:train_station_traintype_changelist"
        )

        response = self.client.get(url)

        self.assertContains(response, str(train_type))

    def test_admin_train_type_search_by_name(self):
        train_type1 = sample_train_type(name="Test_1")
        train_type2 = sample_train_type(name="Test_2")

        url = reverse(
            "admin:train_station_traintype_changelist"
        )

        response = self.client.get(url, {"q": train_type1.name.lower()})

        changelist = response.context["cl"]
        self.assertIn(train_type1, changelist.queryset)
        self.assertNotIn(train_type2, changelist.queryset)

    def test_train_admin_has_require_field(self):
        train = sample_train(name="Test_1")

        url = reverse(
            "admin:train_station_train_changelist"
        )

        response = self.client.get(url)

        self.assertContains(response, train.name)
        self.assertContains(response, train.cargo_num)
        self.assertContains(response, train.places_in_cargo)
        self.assertContains(response, train.train_type)

    def test_admin_train_search_by_name(self):
        train1 = sample_train(name="Test_1")
        train2 = sample_train(name="Test_2")

        url = reverse(
            "admin:train_station_train_changelist"
        )

        response = self.client.get(url, {"q": train1.name.lower()})

        changelist = response.context["cl"]
        self.assertIn(train1, changelist.queryset)
        self.assertNotIn(train2, changelist.queryset)

    def test_admin_train_search_by_train_type_name(self):
        train_type1 = sample_train_type(name="Test_1")
        train_type2 = sample_train_type(name="Test_2")
        train1 = sample_train(name="Test_Train1", train_type=train_type1)
        train2 = sample_train(name="Test_Train2", train_type=train_type2)

        url = reverse(
            "admin:train_station_train_changelist"
        )

        response = self.client.get(url, {"q": train_type1.name.lower()})

        changelist = response.context["cl"]
        self.assertIn(train1, changelist.queryset)
        self.assertNotIn(train2, changelist.queryset)

    def test_admin_train_filter_by_cargo_num(self):
        train1 = sample_train(name="Test_1", cargo_num=10)
        train2 = sample_train(name="Test_2", cargo_num=15)

        url = reverse(
            "admin:train_station_train_changelist"
        )

        response = self.client.get(url, {"cargo_num": train1.cargo_num})

        changelist = response.context["cl"]
        self.assertIn(train1, changelist.queryset)
        self.assertNotIn(train2, changelist.queryset)

    def test_admin_train_filter_by_seats_in_cargo(self):
        train1 = sample_train(name="Test_1", places_in_cargo=10)
        train2 = sample_train(name="Test_2", places_in_cargo=15)

        url = reverse(
            "admin:train_station_train_changelist"
        )

        response = self.client.get(url, {"places_in_cargo": train1.places_in_cargo})

        changelist = response.context["cl"]
        self.assertIn(train1, changelist.queryset)
        self.assertNotIn(train2, changelist.queryset)

    def test_crew_admin_has_require_field(self):
        crew_member = sample_crew(
            first_name="first_name_test", last_name="last_name_test"
        )

        url = reverse(
            "admin:train_station_crew_changelist"
        )

        response = self.client.get(url)

        self.assertContains(response, str(crew_member))

    def test_admin_crew_search_by_first_name_and_last_name(self):
        crew_member1 = sample_crew(
            first_name="first_name_test1", last_name="last_name_test1"
        )
        crew_member2 = sample_crew(
            first_name="first_name_test2", last_name="last_name_test2"
        )

        url = reverse(
            "admin:train_station_crew_changelist"
        )

        response1 = self.client.get(
            url, {"q": crew_member1.first_name.lower()}
        )
        response2 = self.client.get(
            url, {"q": crew_member1.last_name.lower()}
        )

        changelist1 = response1.context["cl"]
        self.assertIn(crew_member1, changelist1.queryset)
        self.assertNotIn(crew_member2, changelist1.queryset)

        changelist2 = response2.context["cl"]
        self.assertIn(crew_member1, changelist2.queryset)
        self.assertNotIn(crew_member2, changelist2.queryset)

    def test_trip_admin_has_require_field(self):
        trip = sample_trip(name="Test_1")

        url = reverse(
            "admin:train_station_trip_changelist"
        )

        response = self.client.get(url)

        self.assertContains(response, trip.route)
        self.assertContains(response, trip.train)
        self.assertIn("departure_time", TripAdmin.list_display)
        self.assertIn("arrival_time", TripAdmin.list_display)

    def test_admin_trip_search_by_route_source_name(self):
        trip1 = sample_trip(name="Test_1")
        trip2 = sample_trip(name="Test_2")

        url = reverse(
            "admin:train_station_trip_changelist"
        )

        response = self.client.get(
            url, {"q": trip1.route.source.name.lower()}
        )

        changelist = response.context["cl"]
        self.assertIn(trip1, changelist.queryset)
        self.assertNotIn(trip2, changelist.queryset)

    def test_admin_trip_filter_by_train_type_id(self):
        train_type = sample_train_type(name="Test_1")
        trip1 = sample_trip(name="Test_Trip_1")
        trip2 = sample_trip(name="Test_Trip_2")
        trip1.train.train_type = train_type
        trip1.train.save()

        url = reverse(
            "admin:train_station_trip_changelist"
        )

        response = self.client.get(
            url, {"train__train_type__id__exact": train_type.id}
        )

        changelist = response.context["cl"]

        self.assertIn(trip1, changelist.queryset)
        self.assertNotIn(trip2, changelist.queryset)

    def test_order_admin_has_require_field(self):
        user = get_user_model().objects.create(
            email="test1@test.test", password="test_password"
        )
        order = sample_order(user=user)

        url = reverse(
            "admin:train_station_order_changelist"
        )

        response = self.client.get(url)

        self.assertContains(response, order.user.email)
        self.assertIn("created_at", OrderAdmin.list_display)

    def test_order_admin_search_by_user_email(self):
        user1 = get_user_model().objects.create(
            email="test1@test.test", password="test_password"
        )
        user2 = get_user_model().objects.create(
            email="test2@test.test", password="test_password"
        )
        order1 = sample_order(user=user1)
        order2 = sample_order(user=user2)

        url = reverse(
            "admin:train_station_order_changelist"
        )

        response = self.client.get(url, {"q": user1.email})

        changelist = response.context["cl"]
        self.assertIn(order1, changelist.queryset)
        self.assertNotIn(order2, changelist.queryset)