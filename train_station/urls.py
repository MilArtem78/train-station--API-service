from django.urls import path
from django.urls.conf import include
from rest_framework import routers

from train_station.views import (
    TrainTypeViewSet,
    StationViewSet,
    CrewViewSet,
    RouteViewSet,
    TrainViewSet,
    TripViewSet,
    OrderViewSet
)

router = routers.DefaultRouter()
router.register("train_types", TrainTypeViewSet)
router.register("stations", StationViewSet)
router.register("crews", CrewViewSet)
router.register("routes", RouteViewSet)
router.register("trains", TrainViewSet)
router.register("trips", TripViewSet)
router.register("orders", OrderViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "train_station"
