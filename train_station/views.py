from django.db.models import Count, F, Q
from rest_framework import mixins, viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
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
from train_station.permissions import IsAdminAllORIsAuthenticatedReadOnly
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
    OrderListSerializer,
    CrewImageSerializer
)


class TrainTypeViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet
):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer
    permission_classes = (IsAdminAllORIsAuthenticatedReadOnly,)


class StationViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet
):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = (IsAdminAllORIsAuthenticatedReadOnly,)


class CrewViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminAllORIsAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "upload_image":
            return CrewImageSerializer

        return CrewSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to a crew member"""
        crew = self.get_object()
        serializer = self.get_serializer(crew, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


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
    permission_classes = (IsAdminAllORIsAuthenticatedReadOnly,)

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
    permission_classes = (IsAdminAllORIsAuthenticatedReadOnly,)

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
    permission_classes = (IsAdminAllORIsAuthenticatedReadOnly,)

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


class OrderPagination(PageNumberPagination):
    page_size = 1
    max_page_size = 100


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
    pagination_class = OrderPagination
    permission_classes = (IsAuthenticated,)

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
