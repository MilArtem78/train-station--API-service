from django.shortcuts import render
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from train_station.models import (
    TrainType,
    Station,
    Crew
)
from train_station.serializers import (
    TrainTypeSerializer,
    StationSerializer,
    CrewSerializer
)


class TrainTypeViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet
):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class StationViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet
):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class CrewViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
