from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from train_station.models import (
    TrainType,
    Station,
    Crew,
    Route,
    Train,
    Trip,
    Ticket,
    Order
)


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ("id", "name", "description")


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude")


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name")


class RouteSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(RouteSerializer, self).validate(attrs)
        Route.validate_route(
            attrs["source"],
            attrs["destination"],
            serializers.ValidationError
        )
        return data

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(
        read_only=True, slug_field="name"
    )
    destination = serializers.SlugRelatedField(
        read_only=True, slug_field="name"
    )


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = ("id", "name", "cargo_num", "places_in_cargo", "train_type")


class TrainListSerializer(TrainSerializer):
    train_type = serializers.SlugRelatedField(
        read_only=True, slug_field="name"
    )

    class Meta:
        model = Train
        fields = (
            "id",
            "name",
            "cargo_num",
            "places_in_cargo",
            "capacity",
            "train_type")


class TrainDetailSerializer(TrainListSerializer):
    train_type = TrainTypeSerializer(read_only=True)


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = "__all__"


class TripListSerializer(TripSerializer):
    crew = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="full_name"
    )
    route = serializers.StringRelatedField()
    train_name = serializers.CharField(
        read_only=True, source="train.name"
    )
    train_type = serializers.CharField(
        read_only=True, source="train.train_type.name"
    )
    train_cargo_num = serializers.IntegerField(
        read_only=True, source="train.cargo_num"
    )
    train_capacity = serializers.IntegerField(
        read_only=True, source="train.capacity"
    )
    tickets_available = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = Trip
        fields = (
            "id",
            "crew",
            "route",
            "departure_time",
            "train_name",
            "train_type",
            "train_cargo_num",
            "train_capacity",
            "tickets_available"
        )


class TicketTakenPlacesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["cargo", "seat"]


class TripDetailSerializer(TripSerializer):
    route = RouteListSerializer(read_only=True)
    train = TrainDetailSerializer(read_only=True)
    taken_places = TicketTakenPlacesSerializer(
        source="tickets", many=True, read_only=True
    )
    crew = CrewSerializer(many=True, read_only=True)

    class Meta:
        model = Trip
        fields = (
            "id",
            "route",
            "train",
            "crew",
            "departure_time",
            "arrival_time",
            "taken_places"
        )


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs)
        Ticket.validate_ticket(
            attrs["cargo"],
            attrs["seat"],
            attrs["trip"].train,
            ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "trip")


class TicketListSerializer(TicketSerializer):
    trip = TripListSerializer(read_only=True)
