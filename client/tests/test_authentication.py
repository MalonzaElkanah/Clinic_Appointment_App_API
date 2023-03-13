from django.urls import reverse
from django.contrib.auth.models import Group

from rest_framework import status
from rest_framework.test import APITestCase

from client.models import MyUser


class BearerAuthenticationTests(APITestCase):
    def setUp(self):
        """
        Create roles and users Objects to be used
        through-out this Authentication Tests Case.
        """

        # Create roles
        role, created = Group.objects.get_or_create(name="ADMIN")

        # Create admin and non-admin user
        user = MyUser.objects.create(
            role=role,
            phone="0712345678",
            verified=True,
            email="adminuser1@myapp.com",
            password="Pass1234",
            username="adminuser1",
            first_name="admin",
            last_name="user1",
        )
        user.set_password(user.password)
        user.save()

    def test_token_authentication(self):
        """
        Ensure a user can generate a valid token
        with token and bearer keyword.
        """

        # generate a valid auth token
        url = reverse("api-token")
        data = {"username": "adminuser1", "password": "Pass1234"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.json().get("token", None))

        # Test the valid token header
        url = reverse("groups_list_create")
        valid_token = response.json()["token"]
        valid_keywords = ["Token", "Bearer"]

        for keyword in valid_keywords:
            auth_token = f"{keyword} {valid_token}"
            response = self.client.get(
                url, HTTP_AUTHORIZATION=auth_token, format="json"
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.json()["results"]), Group.objects.count())

        # Test with Invalid token header
        url = reverse("groups_list_create")
        invalid_keyword = "Baerer"
        invalid_token = "BeStillMyFoolishHeart.DontRuinThisForMe"

        auth_token = f"{invalid_keyword} {valid_token}"
        response = self.client.get(url, HTTP_AUTHORIZATION=auth_token, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIsNone(response.json().get("results", None))

        for keyword in valid_keywords:
            auth_token = f"{keyword} {invalid_token}"
            response = self.client.get(
                url, HTTP_AUTHORIZATION=auth_token, format="json"
            )

            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertIsNone(response.json().get("results", None))
