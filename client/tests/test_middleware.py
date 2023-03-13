from django.urls import reverse
from django.contrib.auth.models import Group

from rest_framework.test import APITestCase

from client.models import ActivityLog, MyUser


class UserLoggerMiddlewareTests(APITestCase):
    def setUp(self):
        """
        Create roles, users Objects to be used
        through-out this Roles Tests Case.
        """

        # Create patient roles and user
        patient_role, created = Group.objects.get_or_create(name="PATIENT")

        user = MyUser.objects.create(
            role=patient_role,
            phone="0723456789",
            verified=True,
            email="p.user1@myapp.com",
            password="Pass1234",
            username="p.user1",
            first_name="user1",
            last_name="p.",
        )
        user.set_password(user.password)
        user.save()

    def test_user_logs(self):
        """
        Ensure the middleware saves logs for any user
        """
        url = reverse("users_list")

        # Ensure log save for unautheticated user
        response = self.client.get(url, format="json")
        latest_log = ActivityLog.objects.last()

        self.assertEqual(response.status_code, int(latest_log.response_code))
        self.assertEqual("GET", latest_log.request_method)
        self.assertEqual(f"http://testserver{url}", latest_log.request_url)
        self.assertEqual(None, latest_log.user)

        # Ensure log save for autheticated user
        username = "p.user1"
        self.client.login(username=username, password="Pass1234")
        response = self.client.get(url, format="json")
        latest_log = ActivityLog.objects.last()

        self.assertEqual(response.status_code, int(latest_log.response_code))
        self.assertEqual("GET", latest_log.request_method)
        self.assertEqual(f"http://testserver{url}", latest_log.request_url)
        self.assertEqual(username, latest_log.user.username)

        self.client.logout()
