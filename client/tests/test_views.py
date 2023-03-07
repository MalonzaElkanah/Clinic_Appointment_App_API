from rest_framework.test import APITestCase


class ListCreateUserViewTests(APITestCase):
    def setUp(self):
        """
        Create roles and users Objects to be used
        through-out this Speciality Tests Case.
        """
        pass

    def test_list_users(self):
        """
        Ensure Admin user can list all users,
        non-admin user can only list their user profile,
        AnonymousUser will return empty user list
        """
        pass
