from django.db import models


class Station(models.Model):
    name = models.CharField(max_length=255, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="source_routes"
    )
    destination = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="destination_routes"
    )
    distance = models.PositiveIntegerField()

    class Meta:
        unique_together = ["source", "destination"]
        ordering = ["source"]

    def __str__(self):
        return f"{self.source} - {self.destination}"


class TrainType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
