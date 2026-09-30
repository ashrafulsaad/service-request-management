from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework.test import APIClient

from accounts.models import User
from .models import Category, ServiceRequest


class ServiceRequestAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        # -----------------------------------------------------
        # USERS
        # -----------------------------------------------------

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

        self.officer2 = User.objects.create_user(
            username="officer2",
            password="testpass123",
            role="officer",
        )

        self.admin = User.objects.create_user(
            username="admin1",
            password="testpass123",
            role="admin",
        )

        # -----------------------------------------------------
        # CATEGORIES
        # -----------------------------------------------------

        self.category = Category.objects.create(
            name="General"
        )

        self.category2 = Category.objects.create(
            name="Health"
        )

        # -----------------------------------------------------
        # SERVICE REQUESTS
        # -----------------------------------------------------

        self.service_request = ServiceRequest.objects.create(
            citizen=self.citizen,
            category=self.category,
            title="Test Request",
            description="Test description",
            priority="medium",
            status="pending",
            assigned_officer=self.officer,
        )

    # =========================================================
    # CHUNK 1 — CATEGORY MANAGEMENT
    # =========================================================

    def test_admin_can_create_category(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            "/api/categories/",
            {"name": "Birth Certificate"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)

    def test_citizen_cannot_create_category(self):
        self.client.force_authenticate(user=self.citizen)

        response = self.client.post(
            "/api/categories/",
            {"name": "Unauthorized Category"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_officer_cannot_create_category(self):
        self.client.force_authenticate(user=self.officer)

        response = self.client.post(
            "/api/categories/",
            {"name": "Unauthorized Category"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_authenticated_user_can_list_categories(self):
        self.client.force_authenticate(user=self.citizen)

        response = self.client.get("/api/categories/")

        self.assertEqual(response.status_code, 200)

    def test_admin_can_delete_unused_category(self):
        category = Category.objects.create(
            name="Unused Category"
        )

        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            f"/api/categories/{category.id}/"
        )

        self.assertEqual(response.status_code, 204)

        self.assertFalse(
            Category.objects.filter(id=category.id).exists()
        )

    def test_cannot_delete_category_used_by_request(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            f"/api/categories/{self.category.id}/"
        )

        self.assertEqual(response.status_code, 400)

        self.assertTrue(
            Category.objects.filter(
                id=self.category.id
            ).exists()
        )

    # =========================================================
    # CHUNK 2 — USER LIST / OFFICER ASSIGNMENT
    # =========================================================

    def test_admin_can_list_officers(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            "/api/users/?role=officer"
        )

        self.assertEqual(response.status_code, 200)

        results = response.data["results"]

        self.assertEqual(len(results), 2)

        for user in results:
            self.assertEqual(user["role"], "officer")

    def test_citizen_cannot_list_users(self):
        self.client.force_authenticate(user=self.citizen)

        response = self.client.get(
            "/api/users/?role=officer"
        )

        self.assertEqual(response.status_code, 403)

    def test_officer_cannot_list_users(self):
        self.client.force_authenticate(user=self.officer)

        response = self.client.get(
            "/api/users/?role=officer"
        )

        self.assertEqual(response.status_code, 403)

    def test_admin_can_assign_officer(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            f"/api/requests/{self.service_request.id}/assign/",
            {"officer_id": self.officer2.id},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.service_request.refresh_from_db()

        self.assertEqual(
            self.service_request.assigned_officer,
            self.officer2,
        )

    def test_admin_can_reassign_officer(self):
        # Initially assigned to officer1.
        self.assertEqual(
            self.service_request.assigned_officer,
            self.officer,
        )

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            f"/api/requests/{self.service_request.id}/assign/",
            {"officer_id": self.officer2.id},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.service_request.refresh_from_db()

        self.assertEqual(
            self.service_request.assigned_officer,
            self.officer2,
        )

    def test_admin_cannot_assign_citizen_as_officer(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            f"/api/requests/{self.service_request.id}/assign/",
            {"officer_id": self.citizen.id},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.service_request.refresh_from_db()

        self.assertEqual(
            self.service_request.assigned_officer,
            self.officer,
        )

    def test_citizen_cannot_assign_officer(self):
        self.client.force_authenticate(user=self.citizen)

        response = self.client.post(
            f"/api/requests/{self.service_request.id}/assign/",
            {"officer_id": self.officer.id},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    # =========================================================
    # CHUNK 3 — REQUEST VISIBILITY
    # =========================================================

    def test_citizen_cannot_see_other_citizen_request(self):
        self.client.force_authenticate(
            user=self.other_citizen
        )

        response = self.client.get(
            f"/api/requests/{self.service_request.id}/"
        )

        self.assertEqual(response.status_code, 404)

    def test_citizen_only_sees_own_requests(self):
        ServiceRequest.objects.create(
            citizen=self.other_citizen,
            category=self.category,
            title="Other Citizen Request",
            description="Other description",
            priority="high",
            status="pending",
        )

        self.client.force_authenticate(
            user=self.citizen
        )

        response = self.client.get("/api/requests/")

        self.assertEqual(response.status_code, 200)

        results = response.data["results"]

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0]["title"],
            "Test Request",
        )

    def test_officer_only_sees_assigned_requests(self):
        ServiceRequest.objects.create(
            citizen=self.other_citizen,
            category=self.category,
            title="Unassigned Request",
            description="Another description",
            priority="high",
            status="pending",
        )

        self.client.force_authenticate(
            user=self.officer
        )

        response = self.client.get("/api/requests/")

        self.assertEqual(response.status_code, 200)

        results = response.data["results"]

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0]["title"],
            "Test Request",
        )

    def test_admin_can_see_all_requests(self):
        ServiceRequest.objects.create(
            citizen=self.other_citizen,
            category=self.category,
            title="Second Request",
            description="Second description",
            priority="high",
            status="resolved",
        )

        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.get("/api/requests/")

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data["count"],
            2,
        )

    # =========================================================
    # CHUNK 3 — FILTERING
    # =========================================================

    def test_filter_requests_by_status(self):
        ServiceRequest.objects.create(
            citizen=self.citizen,
            category=self.category,
            title="Resolved Request",
            description="Resolved description",
            priority="high",
            status="resolved",
            assigned_officer=self.officer,
        )

        self.client.force_authenticate(
            user=self.citizen
        )

        response = self.client.get(
            "/api/requests/?status=pending"
        )

        self.assertEqual(response.status_code, 200)

        results = response.data["results"]

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0]["status"],
            "pending",
        )

    def test_filter_requests_by_priority(self):
        ServiceRequest.objects.create(
            citizen=self.citizen,
            category=self.category,
            title="High Priority Request",
            description="High priority description",
            priority="high",
            status="pending",
            assigned_officer=self.officer,
        )

        self.client.force_authenticate(
            user=self.citizen
        )

        response = self.client.get(
            "/api/requests/?priority=high"
        )

        self.assertEqual(response.status_code, 200)

        results = response.data["results"]

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0]["priority"],
            "high",
        )

    def test_filter_requests_by_category(self):
        ServiceRequest.objects.create(
            citizen=self.citizen,
            category=self.category2,
            title="Health Request",
            description="Health description",
            priority="low",
            status="pending",
        )

        self.client.force_authenticate(
            user=self.citizen
        )

        response = self.client.get(
            f"/api/requests/?category={self.category2.id}"
        )

        self.assertEqual(response.status_code, 200)

        results = response.data["results"]

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0]["title"],
            "Health Request",
        )

    def test_filter_requests_by_assigned_officer(self):
        self.client.force_authenticate(
            user=self.officer
        )

        response = self.client.get(
            f"/api/requests/?assigned_officer={self.officer.id}"
        )

        self.assertEqual(response.status_code, 200)

        results = response.data["results"]

        self.assertEqual(len(results), 1)

    # =========================================================
    # CHUNK 3 — SEARCH
    # =========================================================

    def test_search_requests_by_title(self):
        self.client.force_authenticate(
            user=self.citizen
        )

        response = self.client.get(
            "/api/requests/?search=Test"
        )

        self.assertEqual(response.status_code, 200)

        results = response.data["results"]

        self.assertEqual(len(results), 1)

        self.assertEqual(
            results[0]["title"],
            "Test Request",
        )

    # =========================================================
    # CHUNK 3 — ORDERING
    # =========================================================

    def test_ordering_by_priority(self):
        ServiceRequest.objects.create(
            citizen=self.citizen,
            category=self.category,
            title="High Priority",
            description="High priority",
            priority="high",
            status="pending",
        )

        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.get(
            "/api/requests/?ordering=priority"
        )

        self.assertEqual(response.status_code, 200)

        results = response.data["results"]

        self.assertEqual(len(results), 2)

        self.assertEqual(
            results[0]["priority"],
            "high",
        )

    # =========================================================
    # CHUNK 3 — PAGINATION
    # =========================================================

    def test_request_list_is_paginated(self):
        self.client.force_authenticate(
            user=self.citizen
        )

        response = self.client.get(
            "/api/requests/"
        )

        self.assertEqual(response.status_code, 200)

        self.assertIn(
            "count",
            response.data,
        )

        self.assertIn(
            "results",
            response.data,
        )

        self.assertIn(
            "next",
            response.data,
        )

        self.assertIn(
            "previous",
            response.data,
        )

    # =========================================================
    # CHUNK 4 — ADMIN STATISTICS
    # =========================================================

    def test_admin_can_access_statistics(self):
        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.get(
            "/api/admin/stats/"
        )

        self.assertEqual(response.status_code, 200)

    def test_citizen_cannot_access_statistics(self):
        self.client.force_authenticate(
            user=self.citizen
        )

        response = self.client.get(
            "/api/admin/stats/"
        )

        self.assertEqual(response.status_code, 403)

    def test_officer_cannot_access_statistics(self):
        self.client.force_authenticate(
            user=self.officer
        )

        response = self.client.get(
            "/api/admin/stats/"
        )

        self.assertEqual(response.status_code, 403)

    def test_admin_statistics_match_database(self):
        # Current request:
        # pending + medium + General + officer1

        # Second request:
        ServiceRequest.objects.create(
            citizen=self.citizen,
            category=self.category,
            title="High Request",
            description="High description",
            priority="high",
            status="resolved",
            assigned_officer=self.officer2,
        )

        # Third request:
        ServiceRequest.objects.create(
            citizen=self.other_citizen,
            category=self.category2,
            title="Unassigned Request",
            description="Unassigned description",
            priority="low",
            status="pending",
            assigned_officer=None,
        )

        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.get(
            "/api/admin/stats/"
        )

        self.assertEqual(response.status_code, 200)

        data = response.data

        # Total
        self.assertEqual(
            data["total"],
            3,
        )

        # Status
        self.assertEqual(
            data["by_status"]["pending"],
            2,
        )

        self.assertEqual(
            data["by_status"]["resolved"],
            1,
        )

        # Priority
        self.assertEqual(
            data["by_priority"]["medium"],
            1,
        )

        self.assertEqual(
            data["by_priority"]["high"],
            1,
        )

        self.assertEqual(
            data["by_priority"]["low"],
            1,
        )

        # Categories
        self.assertEqual(
            data["by_category"]["General"],
            2,
        )

        self.assertEqual(
            data["by_category"]["Health"],
            1,
        )

        # Officers
        self.assertEqual(
            data["requests_per_officer"]["officer1"],
            1,
        )

        self.assertEqual(
            data["requests_per_officer"]["officer2"],
            1,
        )

        # Unassigned
        self.assertEqual(
            data["unassigned"],
            1,
        )

    # =========================================================
    # ATTACHMENTS
    # =========================================================

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
