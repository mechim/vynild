from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User


class UserTests(APITestCase):

    def setUp(self):
        # Set up a user for testing listing functionality
        self.user = User.objects.create(username="testuser", password="testpassword")
        self.list_url = reverse("user-list")
        self.create_url = reverse("user-create")

    def test_user_list(self):
        # Test listing all users
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["username"], self.user.username)

    def test_user_list_with_id_filter(self):
        # Test retrieving a specific user by ID
        response = self.client.get(self.list_url, {"id": self.user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.user.id)
        self.assertEqual(response.data[0]["username"], self.user.username)

    def test_user_create(self):
        # Test creating a new user
        data = {"username": "newuser", "password": "newpassword"}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], "newuser")

        # Verify the user was created in the database
        self.assertTrue(User.objects.filter(username="newuser").exists())
