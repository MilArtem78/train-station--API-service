from django.urls import path
from django.urls.conf import include
from rest_framework import routers

from train_station.views import (
    TrainTypeViewSet,
    StationViewSet,
    CrewViewSet,
    RouteViewSet
)

router = routers.DefaultRouter()
router.register("train_types", TrainTypeViewSet)
router.register("stations", StationViewSet)
router.register("crews", CrewViewSet)
router.register("routes", RouteViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "train_station"
