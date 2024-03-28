import os
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


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
        Station,
        on_delete=models.CASCADE,
        related_name="source_routes"
    )
    destination = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="destination_routes"
    )
    distance = models.PositiveIntegerField()

    @staticmethod
    def validate_route(source, destination, error_to_raise):
        if source == destination:
            raise error_to_raise(
                {"source_destination": (
                    f"Source({source}) and destination({destination})"
                    f" cannot be the same."
                )
                }
            )

    def clean(self):
        Route.validate_route(self.source, self.destination, ValidationError)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

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


class Train(models.Model):
    name = models.CharField(max_length=255, unique=True)
    cargo_num = models.PositiveIntegerField()
    places_in_cargo = models.PositiveIntegerField()
    train_type = models.ForeignKey(
        TrainType,
        on_delete=models.CASCADE,
        related_name="trains"
    )

    class Meta:
        ordering = ["name"]

    @property
    def capacity(self) -> int:
        return self.cargo_num * self.places_in_cargo

    def __str__(self):
        return self.name


def crew_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.full_name)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads", "crews", filename)


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to=crew_image_file_path, null=True)

    class Meta:
        ordering = ["first_name", "last_name"]
        verbose_name = "Crew member"
        verbose_name_plural = "Crew members"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Trip(models.Model):
    crew = models.ManyToManyField(Crew)
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="trips"
    )
    train = models.ForeignKey(
        Train,
        on_delete=models.CASCADE,
        related_name="trips"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    class Meta:
        ordering = ["-departure_time"]

    def __str__(self):
        return (
            f"Trip {self.route.source} - {self.route.destination}, "
            f" train — {self.train.name}, "
            f"[{self.departure_time} - {self.arrival_time}]"
        )


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.created_at)


class Ticket(models.Model):
    cargo = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    @staticmethod
    def validate_ticket(cargo, seat, train, error_to_raise):
        for ticket_attr_value, ticket_attr_name, train_attr_name in [
            (cargo, "cargo", "cargo_num"),
            (seat, "seat", "places_in_cargo"),
        ]:
            count_attrs = getattr(train, train_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name:
                            f"{ticket_attr_name} "
                            f"number must be in available range: "
                            f"(1, {train_attr_name}): "
                            f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.cargo,
            self.seat,
            self.trip.train,
            ValidationError,
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        unique_together = ("trip", "cargo", "seat")
        ordering = ["cargo", "seat"]

    def __str__(self):
        return (
            f"{str(self.trip)} (cargo: {self.cargo}, seat: {self.seat})"
        )
