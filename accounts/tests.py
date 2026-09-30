from django.test import TestCase

# Create your tests here.
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class AuthTests(APITestCase):

    def test_register(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "TestPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login(self):
        User.objects.create_user(
            username="loginuser",
            email="login@example.com",
            password="TestPassword123!",
        )

        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "loginuser",
                "password": "TestPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_wrong_password(self):
        User.objects.create_user(
            username="wrongpass",
            email="wrong@example.com",
            password="CorrectPassword123!",
        )

        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "wrongpass",
                "password": "WrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_without_token(self):
        response = self.client.get("/api/auth/me/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_role_restricted_endpoint(self):
        User.objects.create_user(
            username="regularuser",
            email="regular@example.com",
            password="TestPassword123!",
            role=User.Role.CITIZEN,
        )

        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "regularuser",
                "password": "TestPassword123!",
            },
            format="json",
        )

        access_token = response.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

        response = self.client.post(
            "/api/auth/officers/",
            {
                "username": "anotherofficer",
                "email": "another@example.com",
                "password": "OfficerPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
