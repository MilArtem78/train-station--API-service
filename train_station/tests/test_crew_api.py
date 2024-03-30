import os
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from train_station.serializers import (
    CrewSerializer
)
from .create_sample_models import sample_crew, detail_url, sample_trip
from train_station.models import Crew

CREW_URL = reverse("train_station:crew-list")


def image_upload_url(crew_id):
    """Return URL for recipe image upload"""
    return reverse("train_station:crew-upload-image", args=[crew_id])


class UnauthenticatedCrewApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(CREW_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCrewApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="test_password"
        )
        self.client.force_authenticate(self.user)

    def test_list_crew(self):
        sample_crew()
        sample_crew(
            first_name="first_name_test",
            last_name="last_name_test"
        )

        response = self.client.get(CREW_URL)

        crew_members = Crew.objects.all()
        serializers = CrewSerializer(crew_members, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializers.data)

    def test_create_crew_forbidden(self):
        response = self.client.post(CREW_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_crew_api_has_only_get_and_post_methods(self):
        response = self.client.post(CREW_URL)
        allowed_methods = response.headers["Allow"]
        forbidden_methods = ["PATCH", "PUT", "DELETE"]

        self.assertIn("GET", allowed_methods)
        self.assertIn("POST", allowed_methods)
        for method in forbidden_methods:
            self.assertNotIn(method, allowed_methods)


class AdminCrewApi(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.admin = get_user_model().objects.create_user(
            email="test@test.test", password="test_password", is_staff=True
        )
        self.client.force_authenticate(self.admin)

    def test_admin_can_create_crew(self):
        payload = {
            "first_name": "first_name_test",
            "last_name": "last_name_test"
        }
        response = self.client.post(CREW_URL, payload)
        crew = Crew.objects.get(id=response.data["id"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(payload[key], getattr(crew, key))


class CrewImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@test.test", "password_test"
        )
        self.client.force_authenticate(self.user)
        self.crew = sample_crew()
        self.trip = sample_trip("Test")

    def tearDown(self):
        self.crew.image.delete()

    def test_upload_image_to_crew(self):
        """Test uploading an image to crew"""
        url = image_upload_url(self.crew.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            response = self.client.post(
                url,
                {"image": ntf},
                format="multipart"
            )
        self.crew.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("image", response.data)
        self.assertTrue(os.path.exists(self.crew.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.crew.id)
        response = self.client.post(
            url,
            {"image": "not image"},
            format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_crew_list(self):
        url = CREW_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            response = self.client.post(
                url,
                {
                    "first_name": "first_name_test",
                    "last_name": "last_name_test",
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        crew = Crew.objects.get(
            first_name="first_name_test",
            last_name="last_name_test"
        )
        self.assertTrue(crew.image)

    def test_image_url_is_shown_on_crew_detail(self):
        url = image_upload_url(self.crew.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        response = self.client.get(detail_url("crew", self.crew.id))

        self.assertIn("image", response.data)

    def test_image_url_is_shown_on_crew_list(self):
        url = image_upload_url(self.crew.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        response = self.client.get(CREW_URL)

        self.assertIn("image", response.data[0].keys())

    def test_image_url_is_shown_on_trip_detail(self):
        self.trip.crew.add(self.crew)
        url = image_upload_url(self.crew.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        response = self.client.get(detail_url("trip", self.trip.id))

        self.assertIn("image", response.data["crew"][0].keys())

    def test_delete_crew_not_allowed(self):
        url = detail_url("crew", self.crew.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_movie_not_allowed(self):
        url = detail_url("crew", self.crew.id)
        updated = {
            "first_name": "TEST"
        }

        response = self.client.put(url, data=updated)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
