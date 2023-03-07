from django.urls import reverse
from django.contrib.auth.models import Group

from rest_framework import status
from rest_framework.test import APITestCase

from administrator.models import Speciality, AdminInvite
from client.models import MyUser

from mylib import token


class SpecialityAPITests(APITestCase):
    def setUp(self):
        """
        Create roles, users and Speciality Objects to be used
        through-out this Speciality Tests Case.
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

        # Create Speciality Objects
        Speciality.objects.create(name="DocSpeciality1")
        Speciality.objects.create(name="DocSpeciality2")

    def test_list_speciality(self):
        """
        Ensure we can list doctor speciality by any user.
        """

        url = reverse("speciality_list_create")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), Speciality.objects.count())

    def test_create_speciality(self):
        """
        Ensure we can create a doctor speciality by admin user only.
        """

        url = reverse("speciality_list_create")
        data = {"name": "TestSpeciality"}

        # Test if unautheticated user can create
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Speciality.objects.count(), 2)

        # Test if non-admin user can create
        self.client.login(username="p.user1", password="Pass1234")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Speciality.objects.count(), 2)
        self.client.logout()

        # Test if admin user can create
        self.client.login(username="adminuser1", password="Pass1234")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Speciality.objects.count(), 3)
        self.assertEqual(Speciality.objects.last().name, "TestSpeciality")
        self.client.logout()

    def test_retrieve_speciality(self):
        """
        Ensure we can retrieve a doctor speciality by admin user only.
        """

        speciality1 = Speciality.objects.get(name="DocSpeciality1")
        url = reverse("speciality_retrieve_update_destroy", args=(speciality1.id,))

        # Test if unautheticated user can retrieve
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("name", None), None)

        # Test if non-admin user can retrieve
        self.client.login(username="p.user1", password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get("name", None), None)
        self.client.logout()

        # Test if admin user can retrieve
        self.client.login(username="adminuser1", password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["name"], speciality1.name)
        self.client.logout()

    def test_update_speciality(self):
        """
        Ensure we can update a doctor speciality by admin user only.
        """

        data = {"name": "TestSpecialityUpdate"}
        speciality1 = Speciality.objects.get(name="DocSpeciality1")
        url = reverse("speciality_retrieve_update_destroy", args=(speciality1.id,))

        # Test if unautheticated user can update
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(
            Speciality.objects.get(id=speciality1.id).name, "TestSpecialityUpdate"
        )

        # Test if non-admin user can update
        self.client.login(username="p.user1", password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Speciality.objects.get(id=speciality1.id).name, "TestSpecialityUpdate"
        )
        self.client.logout()

        # Test if admin user can update
        self.client.login(username="adminuser1", password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Speciality.objects.get(id=speciality1.id).name, "TestSpecialityUpdate"
        )
        self.client.logout()

    def test_destroy_speciality(self):
        """
        Ensure we can delete a doctor speciality by admin user only.
        """

        speciality1 = Speciality.objects.get(name="DocSpeciality1")
        url = reverse("speciality_retrieve_update_destroy", args=(speciality1.id,))

        # Test if unautheticated user can delete
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Speciality.objects.filter(id=speciality1.id).count(), 1)

        # Test if non-admin user can retrieve
        self.client.login(username="p.user1", password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Speciality.objects.filter(id=speciality1.id).count(), 1)
        self.client.logout()

        # Test if admin user can retrieve
        self.client.login(username="adminuser1", password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Speciality.objects.filter(id=speciality1.id).count(), 0)
        self.client.logout()


class AdminInvitesAPITests(APITestCase):
    def setUp(self):
        """
        Create admin role, user with admin role and AdminInvite Objects
        to aid in testing admin invites
        """

        # Create admin and patient role
        admin_role, created = Group.objects.get_or_create(name="ADMIN")
        patient_role, created = Group.objects.get_or_create(name="PATIENT")

        # Create admin and patient user
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

        # Create AdminInvite Objects
        AdminInvite.objects.create(
            email="user2@myapp.com", phone_number="0712345679", invite_by=admin_user
        )
        AdminInvite.objects.create(
            email="user1@myapp.com", phone_number="0712345677", invite_by=admin_user
        )
        AdminInvite.objects.create(
            email="user0@myapp.com", phone_number="0712345676", invite_by=admin_user
        )

    def test_list_admin_invites(self):
        """
        Ensure an admin user can list all invites.
        """
        url = reverse("admin_invites_list_create")

        # Test if unautheticated user can retrieve
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("results", None), None)

        # Test if non-admin user can retrieve
        self.client.login(username="p.user1", password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get("results", None), None)
        self.client.logout()

        # Test if admin user can list admin-invites
        self.client.login(username="adminuser1", password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), AdminInvite.objects.count())
        self.client.logout()

    def test_create_admin_invite(self):
        """
        Ensure an admin user can create an admin invite.
        """
        url = reverse("admin_invites_list_create")
        data = {"email": "user3@myapp.com", "phone_number": "0712345671"}

        # Test if unautheticated user can create an invite
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(AdminInvite.objects.count(), 3)

        # Test if non-admin user can create
        self.client.login(username="p.user1", password="Pass1234")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(AdminInvite.objects.count(), 3)
        self.client.logout()

        # Test if admin user can create admin-invites
        self.client.login(username="adminuser1", password="Pass1234")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AdminInvite.objects.count(), 4)
        self.assertEqual(AdminInvite.objects.last().email, "user3@myapp.com")
        self.client.logout()

    def test_retrieve_admin_invite(self):
        """
        Ensure an admin-user can view specific admin invite
        in detailed.
        """
        admin_invite = AdminInvite.objects.get(email="user2@myapp.com")
        url = reverse("admin_invites_retrieve_destroy", args=(admin_invite.id,))

        # Test if unautheticated user can retrieve admin-invite
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("email", None), None)

        # Test if non-admin user can retrieve admin-invite
        self.client.login(username="p.user1", password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get("email", None), None)
        self.client.logout()

        # Test if admin user can retrieve a specific admin-invite
        self.client.login(username="adminuser1", password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["email"], admin_invite.email)
        self.client.logout()

    def test_delete_admin_invite(self):
        """
        Ensure we can delete an admin invite
        by admin user only.
        """
        admin_invite = AdminInvite.objects.get(email="user2@myapp.com")
        url = reverse("admin_invites_retrieve_destroy", args=(admin_invite.id,))

        # Test if unautheticated user can delete
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(AdminInvite.objects.filter(id=admin_invite.id).count(), 1)

        # Test if non-admin user can retrieve
        self.client.login(username="p.user1", password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(AdminInvite.objects.filter(id=admin_invite.id).count(), 1)
        self.client.logout()

        # Test if admin user can delete a specific admin-invite
        self.client.login(username="adminuser1", password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(AdminInvite.objects.filter(id=admin_invite.id).count(), 0)
        self.client.logout()

    def test_accept_admin_invite(self):
        """
        Ensure invited email/user can accept an admin invite.
        """

        admin_invite = AdminInvite.objects.get(email="user1@myapp.com")
        str_token = token.encode(
            admin_invite.email, expiration_seconds=(60 * 60 * 24 * 7)
        )
        url = f"{reverse('admin_invites_accept', args=(admin_invite.id,))}?token={str_token}"

        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json()["detail"],
            "Invite Accepted. Code to setup your account has been sent to your email.",
        )
        self.assertEqual(AdminInvite.objects.get(id=admin_invite.id).status, "ACCEPTED")
        self.assertEqual(MyUser.objects.filter(email=admin_invite.email).count(), 1)

    def test_reject_admin_invite(self):
        """
        Ensure invited email/user can reject an admin invite.
        """

        admin_invite = AdminInvite.objects.get(email="user0@myapp.com")
        str_token = token.encode(
            admin_invite.email, expiration_seconds=(60 * 60 * 24 * 7)
        )
        url = f"{reverse('admin_invites_reject', args=(admin_invite.id,))}?token={str_token}"

        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["detail"], "Invite Rejected!")
        self.assertEqual(AdminInvite.objects.get(id=admin_invite.id).status, "REJECTED")
        self.assertEqual(MyUser.objects.filter(email=admin_invite.email).count(), 0)
