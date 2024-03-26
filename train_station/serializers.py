from rest_framework import serializers

from train_station.models import TrainType


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ("id", "name", "description")
