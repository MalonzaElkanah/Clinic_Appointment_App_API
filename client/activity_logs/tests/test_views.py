from django.urls import reverse
from django.contrib.auth.models import Group

from rest_framework import status
from rest_framework.test import APITestCase

from client.models import MyUser, ActivityLog


class ListExportActivityLogsViewTests(APITestCase):
    def setUp(self):
        """
        Create roles and users Objects to be used
        through-out this Activity Logs Tests Case.
        """

        # Create admin and patient roles
        admin_role, created = Group.objects.get_or_create(name="ADMIN")
        patient_role, created = Group.objects.get_or_create(name="PATIENT")

        # Create admin and non-admin user
        admin_user = MyUser.objects.create(
            role=admin_role,
            phone="0712345678",
            verified=True,
            email="adminuser1@myapp.com",
            password="Pass1234",
            username="adminuser1",
            first_name="admin",
            last_name="user1",
        )
        admin_user.set_password(admin_user.password)
        admin_user.save()

        non_admin_user = MyUser.objects.create(
            role=patient_role,
            phone="0723456789",
            verified=True,
            email="p.user1@myapp.com",
            password="Pass1234",
            username="p.user1",
            first_name="user1",
            last_name="p.",
        )
        non_admin_user.set_password(non_admin_user.password)
        non_admin_user.save()

        # Create MyUser Objects
        MyUser.objects.create(
            phone="0723456781",
            email="user2@myapp.com",
            password="Pass1234",
            username="user2",
            first_name="user2",
        )

    def test_list_activity_logs(self):
        """
        Ensure Admin user can list activity logs,
        AnonymousUser and non-admin user cannot list activity logs
        """
        url = reverse("activity_log_list")

        # check if AnonymousUser will return error
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIsNone(response.json().get("results", None))

        # check non-admin user will return error
        self.client.login(username="p.user1", password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIsNone(response.json().get("results", None))
        self.client.logout()

        # check Admin user can list all users
        self.client.login(username="adminuser1", password="Pass1234")
        logs_count = ActivityLog.objects.count()
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), logs_count)
        self.client.logout()

    def test_export_activity_logs(self):
        """
        Ensure Admin user can list activity logs,
        AnonymousUser and non-admin user cannot list activity logs
        """
        url = reverse("activity_log_export")

        # check if AnonymousUser will return error
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(
            response.headers["Content-Type"], "application/vnd.ms-excel"
        )
        self.assertIsNone(response.json().get("results", None))

        # check non-admin user will return error
        self.client.login(username="p.user1", password="Pass1234")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            response.headers["Content-Type"], "application/vnd.ms-excel"
        )
        self.assertIsNone(response.json().get("results", None))
        self.client.logout()

        # check Admin user can list all users
        self.client.login(username="adminuser1", password="Pass1234")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "application/vnd.ms-excel")
        self.client.logout()
