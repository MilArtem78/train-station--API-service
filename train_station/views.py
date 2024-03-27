from django.db.models import Count, F, Q
from rest_framework import mixins, viewsets
from rest_framework.viewsets import GenericViewSet

from train_station.models import (
    TrainType,
    Station,
    Crew,
    Route,
    Train,
    Trip,
    Order
)
from train_station.serializers import (
    TrainTypeSerializer,
    StationSerializer,
    CrewSerializer,
    RouteSerializer,
    RouteListSerializer,
    TrainSerializer,
    TrainListSerializer,
    TrainDetailSerializer,
    TripSerializer,
    TripListSerializer,
    TripDetailSerializer,
    OrderSerializer,
    OrderListSerializer
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


class RouteViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = Route.objects.select_related(
        "source", "destination"
    )
    serializer_class = RouteSerializer

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return RouteListSerializer
        return RouteSerializer


class TrainViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Train.objects.select_related("train_type")
    serializer_class = TrainSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return TrainListSerializer
        if self.action == "retrieve":
            return TrainDetailSerializer
        return TrainSerializer

    @staticmethod
    def _params_to_ints(qs: str):
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get("name")
        train_type = self.request.query_params.get("train_type")
        if train_type:
            train_types_ids = self._params_to_ints(train_type)
            queryset = queryset.filter(train_type__id__in=train_types_ids)
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.select_related(
        "train__train_type",
        "route__source",
        "route__destination"
    ).prefetch_related(
        "crew"
    ).annotate(
        tickets_available=(
                F("train__cargo_num")
                * F("train__places_in_cargo")
                - Count("tickets")
        )
    )
    serializer_class = TripSerializer

    def get_queryset(self):
        queryset = self.queryset
        departure_date = self.request.query_params.get("departure_date")
        route = self.request.query_params.get("route")
        if departure_date:
            queryset = queryset.filter(
                departure_time__date=departure_date
            )
        if route:
            queryset = queryset.filter(
                Q(route__source__name__icontains=route) |
                Q(route__destination__name__icontains=route)
            )
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return TripListSerializer
        if self.action == "retrieve":
            return TripDetailSerializer
        return TripSerializer


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = Order.objects.prefetch_related(
        "tickets__trip__train",
        "tickets__trip__route__source",
        "tickets__trip__route__destination",
        "tickets__trip__crew",
    )
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        serializer = self.serializer_class
        if self.action == "list":
            serializer = OrderListSerializer
        return serializer
