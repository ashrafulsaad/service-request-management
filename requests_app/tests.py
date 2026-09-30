from django.test import TestCase

# Create your tests here.
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from rest_framework.test import APIClient

from accounts.models import User
from .models import Category, ServiceRequest


class ServiceRequestAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.citizen = User.objects.create_user(
            username="citizen1",
            password="testpass123",
            role="citizen",
        )

        self.other_citizen = User.objects.create_user(
            username="citizen2",
            password="testpass123",
            role="citizen",
        )

        self.officer = User.objects.create_user(
            username="officer1",
            password="testpass123",
            role="officer",
        )

        self.admin = User.objects.create_user(
            username="admin1",
            password="testpass123",
            role="admin",
        )

        self.category = Category.objects.create(
            name="General"
        )

        self.service_request = ServiceRequest.objects.create(
            citizen=self.citizen,
            category=self.category,
            title="Test Request",
            description="Test description",
            priority="medium",
            status="pending",
            assigned_officer=self.officer,
        )

    def test_citizen_cannot_see_other_citizen_request(self):
        self.client.force_authenticate(
            user=self.other_citizen
        )

        response = self.client.get(
            f"/api/requests/{self.service_request.id}/"
        )

        self.assertEqual(response.status_code, 404)

    def test_citizen_cannot_assign_officer(self):
        self.client.force_authenticate(
            user=self.citizen
        )

        response = self.client.post(
            f"/api/requests/{self.service_request.id}/assign/",
            {
                "officer_id": self.officer.id
            },
        )

        self.assertEqual(response.status_code, 403)

    def test_citizen_can_upload_attachment(self):
        self.client.force_authenticate(
            user=self.citizen
        )

        file = SimpleUploadedFile(
            "test.pdf",
            b"Test PDF content",
            content_type="application/pdf",
        )

        response = self.client.post(
            f"/api/requests/{self.service_request.id}/attachments/",
            {"file": file},
            format="multipart",
        )

        self.assertEqual(response.status_code, 201)
