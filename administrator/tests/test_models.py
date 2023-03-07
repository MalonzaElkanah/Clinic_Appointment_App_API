from django.db import IntegrityError
from rest_framework.test import APITestCase

from administrator.models import Speciality


class SpecialityModelTests(APITestCase):
    def setUp(self):
        """
        Create Speciality Objects to be used
        through-out this Speciality Tests Case.
        """
        pass

    def test_unique_speciality_name(self):
        """
        Check if name attribute of a speciality objects
        are saved unique in the database
        """
        name = "Speciality-Name"

        Speciality.objects.create(name=name)
        self.assertEqual(Speciality.objects.filter(name=name).count(), 1)

        with self.assertRaisesMessage(IntegrityError, ""):
            Speciality.objects.create(name=name)
