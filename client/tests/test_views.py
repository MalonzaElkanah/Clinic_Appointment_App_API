from django.urls import reverse
from django.contrib.auth.models import Group

from rest_framework import status
from rest_framework.test import APITestCase

from client.models import MyUser

from random import randint


class ListRetrieveDestroyUsersViewTests(APITestCase):
    def setUp(self):
        """
        Create roles and users Objects to be used
        through-out this Users Tests Case.
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

    def test_list_users(self):
        """
        Ensure Admin user can list all users,
        non-admin user can only list their user profile,
        AnonymousUser will return empty user list
        """
        url = reverse("users_list")

        # check Admin user can list all users
        self.client.login(username="adminuser1", password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), MyUser.objects.count())
        self.client.logout()

        # check non-admin user can only list their user profile
        self.client.login(username="p.user1", password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 1)
        self.assertEqual(
            response.json()["results"][0]["email"],
            MyUser.objects.get(username="p.user1").email,
        )
        self.client.logout()

        # check if AnonymousUser will return empty user list
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 0)

    def test_retrieve_user(self):
        """
        Ensure Admin user can retrieve any users,
        other users should return Forbidden response
        """
        user = MyUser.objects.get(email="user2@myapp.com")
        url = reverse("users_retrieve_destroy", args=(user.id,))

        # Test if unautheticated user can retrieve requested user
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("email", None), None)

        # Test if non-admin user can retrieve requested user
        self.client.login(username="p.user1", password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get("email", None), None)
        self.client.logout()

        # Test if admin user can retrieve requested user
        self.client.login(username="adminuser1", password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["email"], user.email)
        self.client.logout()

    def test_delete_user(self):
        """
        Ensure Admin user can delete users,
        other users should return Forbidden response
        """
        user = MyUser.objects.get(email="user2@myapp.com")
        url = reverse("users_retrieve_destroy", args=(user.id,))

        # Test if unautheticated user can delete
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(MyUser.objects.filter(id=user.id).count(), 1)

        # Test if non-admin user can retrieve
        self.client.login(username="p.user1", password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(MyUser.objects.filter(id=user.id).count(), 1)
        self.client.logout()

        # Test if admin user can retrieve
        self.client.login(username="adminuser1", password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(MyUser.objects.filter(id=user.id).count(), 0)
        self.client.logout()


class RetrieveUpdateMyProfileViewTests(APITestCase):
    def setUp(self):
        """
        Create role and user Object to be used
        through-out this Users Tests Case.
        """

        # Create patient role
        patient_role, created = Group.objects.get_or_create(name="PATIENT")

        # Create user
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

    def test_retrieve_profile(self):
        """
        Ensure authenticated user can retrieve their own profile,
        """

        url = reverse("myprofile_retrieve_update")
        username = "p.user1"

        self.client.login(username=username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["username"], username)
        self.client.logout()

    def test_update_profile(self):
        """
        Ensure authenticated user can update their own profile,
        """

        url = reverse("myprofile_retrieve_update")
        username = "p.user1"
        data = {
            "email": "p.user1@myapp.com",
            "phone": "0712345674",
            "street": "221 baker street",
        }

        self.client.login(username=username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check updated values
        for key, value in data.items():
            self.assertEqual(response.json()[key], value)

        # No Email Updates: requires verification
        data = {
            "email": "p.user2@myapp.com",
            "phone": "0712345675",
            "street": "221 silcon street",
        }
        response = self.client.put(url, data, format="json")
        user = MyUser.objects.get(username=username)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(user.email, data["email"])

        # No Partial Updates on required fields
        data = {"email": "p.user7@myapp.com", "street": "2233 silcon street"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user = MyUser.objects.get(username=username)

        for key, value in data.items():
            self.assertNotEqual(data[key], user.serializable_value(field_name=key))

        self.client.logout()


class ChangePasswordViewTests(APITestCase):
    def setUp(self):
        """
        Create role and user Object to be used
        through-out this Change User Password Tests Case.
        """

        # Create patient role
        patient_role, created = Group.objects.get_or_create(name="PATIENT")

        # Create user
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

    def test_change_password(self):
        """
        Check if authenticated user can change their password
        """

        url = reverse("client_change_password")
        username = "p.user1"

        self.client.login(username=username, password="Pass1234")

        # Check if password will change if old_password is Wrong
        data = {"old_password": "1234Pass", "new_password": "Secret1234"}
        response = self.client.put(url, data, format="json")
        user = MyUser.objects.get(username=username)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIs(user.check_password(data["old_password"]), False)
        self.assertIs(user.check_password(data["new_password"]), False)
        self.assertIs(user.check_password("Pass1234"), True)

        # Check if password will change if old_password is Correct
        data = {"old_password": "Pass1234", "new_password": "Secret1234"}
        response = self.client.put(url, data, format="json")
        user = MyUser.objects.get(username=username)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIs(user.check_password(data["old_password"]), False)
        self.assertIs(user.check_password(data["new_password"]), True)
        self.assertIs(user.check_password("Pass1234"), False)

        self.client.logout()


class ForgotAndResetPasswordViewTests(APITestCase):
    def setUp(self):
        """
        Create role and user Object to be used
        through-out this Recover user password Tests Case.
        """

        # Create patient role
        patient_role, created = Group.objects.get_or_create(name="PATIENT")

        # Create user
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

    def test_forgot_password(self):
        url = reverse("client_forgot_password")

        # Forgot password Request with unexisting user email
        email = "notfound@myapp.com"
        data = {"email": email}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Forgot password request with existing user
        email = "p.user1@myapp.com"
        data = {"email": email}
        response = self.client.post(url, data, format="json")
        user = MyUser.objects.get(email=email)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(user.reset_code)

    def test_reset_password(self):
        url = reverse("client_reset_password")
        user = MyUser.objects.get(username="p.user1")

        if user.reset_code in [None, ""]:
            reset_code = randint(111111, 999999)
            user.reset_code = reset_code
            user.save()

        data = {"new_password": "Secret1234", "reset_code": reset_code}

        response = self.client.post(url, data, format="json")
        user = MyUser.objects.get(username="p.user1")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(user.reset_code)
        self.assertIs(user.check_password("Pass1234"), False)
        self.assertIs(user.check_password("Secret1234"), True)
        self.assertIs(user.check_password("RandPass1234"), False)

        # Send wrong reset code
        data = {"new_password": "Secret1234", "reset_code": reset_code}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # TODO
        # Two accounts with same reset code


class ListCreateRetrieveUpdateDestroyGroupViewTests(APITestCase):
    def setUp(self):
        """
        Create roles, users and Group/Role Objects to be used
        through-out this Roles Tests Case.
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

        Group.objects.get_or_create(name="TEST")
        Group.objects.get_or_create(name="TEST1")

    def test_list_roles(self):
        """
        Ensure we can list roles by admin user.
        """
        url = reverse("groups_list_create")

        # Test if unautheticated user can list roles
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("results", None), None)

        # Test if non-admin user can list roles
        self.client.login(username="p.user1", password="Pass1234")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("results", None), None)
        self.client.logout()

        # Test if admin user can list roles
        self.client.login(username="adminuser1", password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), Group.objects.count())
        self.client.logout()

    def test_create_role(self):
        url = reverse("groups_list_create")
        role_num = Group.objects.count()
        data = {"name": "TestRole"}

        # Test if unautheticated user can create
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Group.objects.count(), role_num)

        # Test if non-admin user can create
        self.client.login(username="p.user1", password="Pass1234")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Group.objects.count(), role_num)
        self.client.logout()

        # Test if admin user can create
        self.client.login(username="adminuser1", password="Pass1234")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Group.objects.count(), role_num + 1)
        self.assertEqual(Group.objects.last().name, data["name"])
        self.client.logout()

    def test_retrieve_role(self):
        """
        Ensure we can retrieve a role by admin user only.
        """

        role = Group.objects.get(name="TEST")
        url = reverse("groups_retrieve_update_destroy", args=(role.id,))

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
        self.assertEqual(response.json()["name"], role.name)
        self.client.logout()

    def test_update_role(self):
        """
        Ensure we can update a role by admin user only.
        """

        data = {"name": "TESTUPDATE"}
        role = Group.objects.get(name="TEST")
        url = reverse("groups_retrieve_update_destroy", args=(role.id,))

        # Test if unautheticated user can update
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(Group.objects.get(id=role.id).name, data["name"])

        # Test if non-admin user can update
        self.client.login(username="p.user1", password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(Group.objects.get(id=role.id).name, data["name"])
        self.client.logout()

        # Test if admin user can update
        self.client.login(username="adminuser1", password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Group.objects.get(id=role.id).name, data["name"])
        self.client.logout()

    def test_delete_role(self):
        """
        Ensure we can delete a role by admin user only.
        """

        role = Group.objects.get(name="TEST1")
        url = reverse("groups_retrieve_update_destroy", args=(role.id,))

        # Test if unautheticated user can delete
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Group.objects.filter(id=role.id).exists())

        # Test if non-admin user can retrieve
        self.client.login(username="p.user1", password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Group.objects.filter(id=role.id).exists())
        self.client.logout()

        # Test if admin user can retrieve
        self.client.login(username="adminuser1", password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Group.objects.filter(id=role.id).exists())
        self.client.logout()
