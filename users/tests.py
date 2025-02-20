
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()

class AuthenticationTests(APITestCase):
    def test_user_registration(self):
        data = {"email": "test@example.com", "username": "testuser", "password": "testpass"}
        response = self.client.post("/api/users/register/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_login(self):
        user = User.objects.create_user(email="test@example.com", password="testpass")
        data = {"email": "test@example.com", "password": "testpass"}
        response = self.client.post("/api/users/login/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)