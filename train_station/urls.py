from django.urls import path
from django.urls.conf import include
from rest_framework import routers

from train_station.views import (
    TrainTypeViewSet,
    StationViewSet
)

router = routers.DefaultRouter()
router.register("train_types", TrainTypeViewSet)
router.register("stations", StationViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "train_station"
