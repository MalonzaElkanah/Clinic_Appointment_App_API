from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from clinic.models import (
    Doctor,
    Education,
    Experience,
    Award,
    Membership,
    Registration,
    DoctorSchedule,
    TimeSlot,
    SocialMedia,
    Appointment,
    AppoinmentReview,
    Patient,
    LikedReview,
    Reply,
    LikedReply,
)
from administrator.models import Speciality
from clinic.tests.utils import create_user

import datetime as dt


class ListCreateRetrieveUpdateDestroyDoctorViewTests(APITestCase):
    def setUp(self):
        """
        Create user and Patient Object to be used
        through-out this Patient View Tests Case.
        """
        Doctor.objects.get_or_create(
            user=create_user(role="DOCTOR", enforce_new=True),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        Doctor.objects.get_or_create(
            user=create_user(role="DOCTOR", enforce_new=True),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )

    def test_list_doctor(self):
        """
        Ensure you can list doctors.
        """
        url = reverse("doctor:doctor_list_create")

        # check user can list doctors
        user = create_user(enforce_new=True)
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), Doctor.objects.count())
        self.client.logout()

        # check if AnonymousUser will return empty doctor list
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 0)

    def test_create_doctor(self):
        """
        Ensure you can register as doctor.
        """
        speciality, created = Speciality.objects.get_or_create(name="Test")
        url = reverse("doctor:doctor_list_create")
        data = {
            "user": {
                "email": "newdoc@myapp.com",
                "phone": "0712309876",
                "username": "newdoc",
                "password": "Pass1234",
                "first_name": "newdoc",
            },
            "speciality": speciality.id,
        }
        count = Doctor.objects.count()
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Doctor.objects.last().user.email, data["user"]["email"])
        self.assertEqual(Doctor.objects.count(), count + 1)

        # Create a patient that already exists
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Doctor.objects.count(), count + 1)

    def test_retrieve_doctor(self):
        """
        Ensure a users can retrieve doctor profile.
        """
        doctor, created = Doctor.objects.get_or_create(
            user=create_user(role="DOCTOR", enforce_new=True),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        url = reverse("doctor:doctor_retrieve_update", args=(doctor.id,))

        # Test if unautheticated user can retrieve
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("id", None), None)

        # check if Doctor can get a doctor details
        user = create_user(enforce_new=True)
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], doctor.id)
        self.client.logout()

    def test_update_doctor(self):
        """
        Ensure a doctor can update their profile.
        """
        speciality, created = Speciality.objects.get_or_create(name="Test")
        doctor, created = Doctor.objects.get_or_create(
            user=create_user(name="OldDoc", role="DOCTOR"), speciality=speciality
        )
        url = reverse("doctor:doctor_retrieve_update", args=(doctor.id,))
        data = {
            "user": {
                "email": "newdoc1@myapp.com",
                "phone": "0712319876",
                "first_name": "newpatient",
                "username": "OldDoc",
            },
            "speciality": speciality.id,
        }

        # Test if unautheticated user cannot update
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(
            Doctor.objects.get(id=doctor.id).user.first_name, data["user"]["first_name"]
        )

        # Test if non owner cannot update
        user = create_user(enforce_new=True)
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Doctor.objects.get(id=doctor.id).user.first_name, data["user"]["first_name"]
        )
        self.client.logout()

        # Test if owner can update
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Doctor.objects.get(id=doctor.id).user.first_name, data["user"]["first_name"]
        )
        self.client.logout()

    def test_destroy_doctor(self):
        """
        Ensure a doctor can delete their profile.
        """
        doctor, created = Doctor.objects.get_or_create(
            user=create_user(name="OldDoc1", role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        url = reverse("doctor:doctor_retrieve_update", args=(doctor.id,))

        # Test if unautheticated user cannot delete
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Doctor.objects.filter(id=doctor.id).exists())

        # Test if non-owner cannot retrieve
        user = create_user(enforce_new=True)
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Doctor.objects.filter(id=doctor.id).exists())
        self.client.logout()

        # Test if admin user can retrieve
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Doctor.objects.filter(id=doctor.id).exists())
        self.client.logout()


class EducationViewTests(APITestCase):
    def setUp(self):
        pass

    def test_list_education(self):
        """
        Ensure you can list doctors education.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        for x in range(1, 4):
            Education.objects.create(
                doctor=doctor,
                degree=f"Degree-{x}",
                institute=f"Institute-{x}",
                date_of_completion=dt.date.today() - dt.timedelta(days=(366 * x)),
            )

        doctor2 = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        for x in range(1, 3):
            Education.objects.create(
                doctor=doctor2,
                degree=f"Degree-j{x}",
                institute=f"Institute-j{x}",
                date_of_completion=dt.date.today() - dt.timedelta(days=(366 * 2 * x)),
            )

        url = reverse("doctor:education-list", args=(doctor.id,))

        # Test if unautheticated user cannot list models
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("results", None), None)

        # Test if autheticated user can list models
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.json()["results"]),
            Education.objects.filter(doctor=doctor.id).count(),
        )
        for data in response.json()["results"]:
            self.assertEqual(data["doctor"], doctor.id)
        self.client.logout()

    def test_create_education(self):
        """
        Ensure a doctor can add education details.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        obj_data = {
            "doctor": doctor.id,
            "degree": "Animal Wizardary",
            "institute": "Hogwat Institute",
            "date_of_completion": dt.date.today() - dt.timedelta(days=(366 * 2)),
        }
        obj_count = Education.objects.count()

        url = reverse("doctor:education-list", args=(doctor.id,))

        # Test if unautheticated user can create models
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Education.objects.count(), obj_count)

        # Test if non-doctor user can create models
        user = create_user(role="PATIENT")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Education.objects.count(), obj_count)
        self.client.logout()

        # Test if non-owner doctor can create models
        user = create_user(name="d.user2", role="DOCTOR")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Education.objects.count(), obj_count)
        self.client.logout()

        # Test if owner doctor can create models
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Education.objects.count(), obj_count + 1)
        self.client.logout()

    def test_retrieve_education(self):
        """
        Ensure a users can retrieve doctor education profile.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        education = Education.objects.create(
            doctor=doctor,
            degree="Degree",
            institute="Institute",
            date_of_completion=dt.date.today() - dt.timedelta(days=366),
        )

        url = reverse("doctor:education-detail", args=(doctor.id, education.id))

        # Test if unautheticated user cannot retrieve models
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("id", None), None)

        # Test if autheticated user can retrieve models
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], education.id)
        self.client.logout()

    def test_update_education(self):
        """
        Ensure a doctor can update Education.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        education = Education.objects.create(
            doctor=doctor,
            degree="Degree",
            institute="Institute",
            date_of_completion=dt.date.today() - dt.timedelta(days=366),
        )

        url = reverse("doctor:education-detail", args=(doctor.id, education.id))

        data = {
            "doctor": doctor.id,
            "degree": "DegreeX",
            "institute": "InstituteX",
            "date_of_completion": dt.date.today() - dt.timedelta(days=(366 * 2)),
        }

        # Test if unautheticated user can update
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(
            Education.objects.get(id=education.id).degree, data["degree"]
        )

        # Test if non-doctor user cannot update
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Education.objects.get(id=education.id).degree, data["degree"]
        )
        self.client.logout()

        # Test if non-owner doctor user cannot update
        user = create_user(name="d.user2", role="DOCTOR")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Education.objects.get(id=education.id).degree, data["degree"]
        )
        self.client.logout()

        # Test if owner doctor can create models
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Education.objects.get(id=education.id).degree, data["degree"])
        self.client.logout()

    def test_delete_education(self):
        """
        Ensure a doctor can delete their Education.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        obj = Education.objects.create(
            doctor=doctor,
            degree="Degree",
            institute="Institute",
            date_of_completion=dt.date.today() - dt.timedelta(days=366),
        )

        url = reverse("doctor:education-detail", args=(doctor.id, obj.id))

        # Test if unautheticated user cannot delete
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Education.objects.filter(id=obj.id).exists())

        # Test if non doctor user cannot delete
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Education.objects.filter(id=obj.id).exists())
        self.client.logout()

        # Test if non owner doctor user cannot delete
        user = create_user(name="d.user2", role="DOCTOR")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Education.objects.filter(id=obj.id).exists())
        self.client.logout()

        # Test if owner doctor can destroy
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Education.objects.filter(id=obj.id).exists())
        self.client.logout()


class ExperienceViewTests(APITestCase):
    def setUp(self):
        pass

    def test_list_experience(self):
        """
        Ensure you can list doctors experience.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        for x in range(1, 4):
            Experience.objects.create(
                doctor=doctor,
                designation=f"Doctor-{x}",
                hospital_name=f"Hospital-{x}",
                start_date=dt.date.today() - dt.timedelta(days=(366 * x)),
                end_date=dt.date.today()
                - dt.timedelta(days=(366 * x))
                + dt.timedelta(days=366),
            )

        doctor2 = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        for x in range(1, 3):
            Experience.objects.create(
                doctor=doctor2,
                designation=f"Doctor-j{x}",
                hospital_name=f"Clinic-j{x}",
                start_date=dt.date.today() - dt.timedelta(days=(366 * 2 * x)),
                end_date=dt.date.today()
                - dt.timedelta(days=(366 * 2 * x))
                + dt.timedelta(days=366),
            )

        url = reverse("doctor:experience-list", args=(doctor.id,))

        # Test if unautheticated user cannot list models
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("results", None), None)

        # Test if autheticated user can list models
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.json()["results"]),
            Experience.objects.filter(doctor=doctor.id).count(),
        )
        for data in response.json()["results"]:
            self.assertEqual(data["doctor"], doctor.id)
        self.client.logout()

    def test_create_experience(self):
        """
        Ensure a doctor can add experience details.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        obj_data = {
            "doctor": doctor.id,
            "designation": "Intern",
            "hospital_name": "Racoon City Hospital",
            "start_date": dt.date.today() - dt.timedelta(days=(366 * 2)),
            "end_date": dt.date.today() - dt.timedelta(days=366),
        }
        obj_count = Experience.objects.count()

        url = reverse("doctor:experience-list", args=(doctor.id,))

        # Test if unautheticated user can create models
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Experience.objects.count(), obj_count)

        # Test if non-doctor user can create models
        user = create_user(role="PATIENT")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Experience.objects.count(), obj_count)
        self.client.logout()

        # Test if non-owner doctor can create models
        user = create_user(name="d.user2", role="DOCTOR")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Experience.objects.count(), obj_count)
        self.client.logout()

        # Test if owner doctor can create models
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Experience.objects.count(), obj_count + 1)
        self.client.logout()

    def test_retrieve_experience(self):
        """
        Ensure a users can retrieve doctor experience.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        experience = Experience.objects.create(
            doctor=doctor,
            designation="Doctor x",
            hospital_name="Hospital x",
            start_date=dt.date.today() - dt.timedelta(days=366),
            end_date=dt.date.today(),
        )

        url = reverse("doctor:experience-detail", args=(doctor.id, experience.id))

        # Test if unautheticated user cannot retrieve models
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("id", None), None)

        # Test if autheticated user can retrieve models
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], experience.id)
        self.client.logout()

    def test_update_experience(self):
        """
        Ensure a doctor can update Experience.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        experience = Experience.objects.create(
            doctor=doctor,
            designation="Doctor x",
            hospital_name="Hospital x",
            start_date=dt.date.today() - dt.timedelta(days=366),
            end_date=dt.date.today(),
        )

        url = reverse("doctor:experience-detail", args=(doctor.id, experience.id))

        data = {
            "doctor": doctor.id,
            "designation": "Doctor ReX",
            "hospital_name": "Hospital ReX",
            "start_date": dt.date.today() - dt.timedelta(days=(366 * 2)),
            "end_date": dt.date.today(),
        }

        # Test if unautheticated user can update
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(
            Experience.objects.get(id=experience.id).designation, data["designation"]
        )

        # Test if non-doctor user cannot update
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Experience.objects.get(id=experience.id).designation, data["designation"]
        )
        self.client.logout()

        # Test if non-owner doctor user cannot update
        user = create_user(name="d.user2", role="DOCTOR")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Experience.objects.get(id=experience.id).designation, data["designation"]
        )
        self.client.logout()

        # Test if owner doctor can create models
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Experience.objects.get(id=experience.id).designation, data["designation"]
        )
        self.client.logout()

    def test_delete_experience(self):
        """
        Ensure a doctor can delete their Experience.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        obj = Experience.objects.create(
            doctor=doctor,
            designation="Doctor x",
            hospital_name="Hospital x",
            start_date=dt.date.today() - dt.timedelta(days=366),
            end_date=dt.date.today(),
        )

        url = reverse("doctor:experience-detail", args=(doctor.id, obj.id))

        # Test if unautheticated user cannot delete
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Experience.objects.filter(id=obj.id).exists())

        # Test if non doctor user cannot delete
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Experience.objects.filter(id=obj.id).exists())
        self.client.logout()

        # Test if non owner doctor user cannot delete
        user = create_user(name="d.user2", role="DOCTOR")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Experience.objects.filter(id=obj.id).exists())
        self.client.logout()

        # Test if owner doctor can destroy
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Experience.objects.filter(id=obj.id).exists())
        self.client.logout()


class AwardViewTests(APITestCase):
    def setUp(self):
        pass

    def test_list_award(self):
        """
        Ensure you can list doctors awards.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        for x in range(1, 4):
            Award.objects.create(
                doctor=doctor,
                award=f"Award-{x}",
                date=dt.date.today() - dt.timedelta(days=(366 * x)),
            )

        doctor2 = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        for x in range(1, 3):
            Award.objects.create(
                doctor=doctor2,
                award=f"Award-j{x}",
                date=dt.date.today() - dt.timedelta(days=(366 * 2 * x)),
            )

        url = reverse("doctor:award-list", args=(doctor.id,))

        # Test if unautheticated user cannot list models
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("results", None), None)

        # Test if autheticated user can list models
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.json()["results"]),
            Award.objects.filter(doctor=doctor.id).count(),
        )
        for data in response.json()["results"]:
            self.assertEqual(data["doctor"], doctor.id)
        self.client.logout()

    def test_create_award(self):
        """
        Ensure a doctor can add award details.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        obj_data = {
            "doctor": doctor.id,
            "award": "Burning Spear",
            "date": dt.date.today() - dt.timedelta(days=366),
        }
        obj_count = Award.objects.count()

        url = reverse("doctor:award-list", args=(doctor.id,))

        # Test if unautheticated user can create models
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Award.objects.count(), obj_count)

        # Test if non-doctor user can create models
        user = create_user(role="PATIENT")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Award.objects.count(), obj_count)
        self.client.logout()

        # Test if non-owner doctor can create models
        user = create_user(name="d.user2", role="DOCTOR")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Award.objects.count(), obj_count)
        self.client.logout()

        # Test if owner doctor can create models
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Award.objects.count(), obj_count + 1)
        self.client.logout()

    def test_retrieve_award(self):
        """
        Ensure a users can retrieve doctor award.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        award = Award.objects.create(
            doctor=doctor,
            award="Award-x",
            date=dt.date.today() - dt.timedelta(days=366),
        )

        url = reverse("doctor:award-detail", args=(doctor.id, award.id))

        # Test if unautheticated user cannot retrieve models
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("id", None), None)

        # Test if autheticated user can retrieve models
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], award.id)
        self.client.logout()

    def test_update_award(self):
        """
        Ensure a doctor can update Award.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        award = Award.objects.create(
            doctor=doctor,
            award="Award-x",
            date=dt.date.today() - dt.timedelta(days=366),
        )

        url = reverse("doctor:award-detail", args=(doctor.id, award.id))

        data = {
            "doctor": doctor.id,
            "award": "X-Award",
            "date": dt.date.today() - dt.timedelta(days=(366 * 2)),
        }

        # Test if unautheticated user can update
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(Award.objects.get(id=award.id).award, data["award"])

        # Test if non-doctor user cannot update
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(Award.objects.get(id=award.id).award, data["award"])
        self.client.logout()

        # Test if non-owner doctor user cannot update
        user = create_user(name="d.user2", role="DOCTOR")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(Award.objects.get(id=award.id).award, data["award"])
        self.client.logout()

        # Test if owner doctor can create models
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Award.objects.get(id=award.id).award, data["award"])
        self.client.logout()

    def test_delete_award(self):
        """
        Ensure a doctor can delete their Award.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        obj = Award.objects.create(
            doctor=doctor,
            award="Award-x",
            date=dt.date.today() - dt.timedelta(days=366),
        )

        url = reverse("doctor:award-detail", args=(doctor.id, obj.id))

        # Test if unautheticated user cannot delete
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Award.objects.filter(id=obj.id).exists())

        # Test if non doctor user cannot delete
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Award.objects.filter(id=obj.id).exists())
        self.client.logout()

        # Test if non owner doctor user cannot delete
        user = create_user(name="d.user2", role="DOCTOR")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Award.objects.filter(id=obj.id).exists())
        self.client.logout()

        # Test if owner doctor can destroy
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Award.objects.filter(id=obj.id).exists())
        self.client.logout()


class MembershipViewTests(APITestCase):
    def setUp(self):
        pass

    def test_list_membership(self):
        """
        Ensure you can list doctors membership.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        for x in range(1, 4):
            Membership.objects.create(doctor=doctor, membership=f"membership-{x}")

        doctor2 = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        for x in range(1, 3):
            Membership.objects.create(doctor=doctor2, membership=f"membership-j{x}")

        url = reverse("doctor:membership-list", args=(doctor.id,))

        # Test if unautheticated user cannot list models
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("results", None), None)

        # Test if autheticated user can list models
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.json()["results"]),
            Membership.objects.filter(doctor=doctor.id).count(),
        )
        for data in response.json()["results"]:
            self.assertEqual(data["doctor"], doctor.id)
        self.client.logout()

    def test_create_membership(self):
        """
        Ensure a doctor can add membership details.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        obj_data = {"doctor": doctor.id, "membership": "Docs Union"}
        obj_count = Membership.objects.count()

        url = reverse("doctor:membership-list", args=(doctor.id,))

        # Test if unautheticated user can create models
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Membership.objects.count(), obj_count)

        # Test if non-doctor user can create models
        user = create_user(role="PATIENT")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Membership.objects.count(), obj_count)
        self.client.logout()

        # Test if non-owner doctor can create models
        user = create_user(name="d.user2", role="DOCTOR")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Membership.objects.count(), obj_count)
        self.client.logout()

        # Test if owner doctor can create models
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Membership.objects.count(), obj_count + 1)
        self.client.logout()

    def test_retrieve_membership(self):
        """
        Ensure a users can retrieve doctor membership
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        membership = Membership.objects.create(doctor=doctor, membership="Docs Union")

        url = reverse("doctor:membership-detail", args=(doctor.id, membership.id))

        # Test if unautheticated user cannot retrieve models
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("id", None), None)

        # Test if autheticated user can retrieve models
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], membership.id)
        self.client.logout()

    def test_update_membership(self):
        """
        Ensure a doctor can update Membership.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        membership = Membership.objects.create(doctor=doctor, membership="Docs Union")

        url = reverse("doctor:membership-detail", args=(doctor.id, membership.id))

        data = {"doctor": doctor.id, "membership": "Doctors Union"}

        # Test if unautheticated user can update
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(
            Membership.objects.get(id=membership.id).membership, data["membership"]
        )

        # Test if non-doctor user cannot update
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Membership.objects.get(id=membership.id).membership, data["membership"]
        )
        self.client.logout()

        # Test if non-owner doctor user cannot update
        user = create_user(name="d.user2", role="DOCTOR")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Membership.objects.get(id=membership.id).membership, data["membership"]
        )
        self.client.logout()

        # Test if owner doctor can create models
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Membership.objects.get(id=membership.id).membership, data["membership"]
        )
        self.client.logout()

    def test_delete_membership(self):
        """
        Ensure a doctor can delete their Membership.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        obj = Membership.objects.create(doctor=doctor, membership="Docs Union")

        url = reverse("doctor:membership-detail", args=(doctor.id, obj.id))

        # Test if unautheticated user cannot delete
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Membership.objects.filter(id=obj.id).exists())

        # Test if non doctor user cannot delete
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Membership.objects.filter(id=obj.id).exists())
        self.client.logout()

        # Test if non owner doctor user cannot delete
        user = create_user(name="d.user2", role="DOCTOR")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Membership.objects.filter(id=obj.id).exists())
        self.client.logout()

        # Test if owner doctor can destroy
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Membership.objects.filter(id=obj.id).exists())
        self.client.logout()


class RegistrationViewTests(APITestCase):
    def setUp(self):
        pass

    def test_list_registration(self):
        """
        Ensure you can list doctors registrations.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        for x in range(1, 4):
            Registration.objects.create(
                doctor=doctor,
                registration=f"Registration-{x}",
                date=dt.date.today() - dt.timedelta(days=(366 * x)),
            )

        doctor2 = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        for x in range(1, 3):
            Registration.objects.create(
                doctor=doctor2,
                registration=f"Registration-j{x}",
                date=dt.date.today() - dt.timedelta(days=(366 * 2 * x)),
            )

        url = reverse("doctor:registration-list", args=(doctor.id,))

        # Test if unautheticated user cannot list models
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("results", None), None)

        # Test if autheticated user can list models
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.json()["results"]),
            Registration.objects.filter(doctor=doctor.id).count(),
        )
        for data in response.json()["results"]:
            self.assertEqual(data["doctor"], doctor.id)
        self.client.logout()

    def test_create_registration(self):
        """
        Ensure a doctor can add registration details.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        obj_data = {
            "doctor": doctor.id,
            "registration": "Registration x",
            "date": dt.date.today() - dt.timedelta(days=366),
        }
        obj_count = Registration.objects.count()

        url = reverse("doctor:registration-list", args=(doctor.id,))

        # Test if unautheticated user can create models
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Registration.objects.count(), obj_count)

        # Test if non-doctor user can create models
        user = create_user(role="PATIENT")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Registration.objects.count(), obj_count)
        self.client.logout()

        # Test if non-owner doctor can create models
        user = create_user(name="d.user2", role="DOCTOR")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Registration.objects.count(), obj_count)
        self.client.logout()

        # Test if owner doctor can create models
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Registration.objects.count(), obj_count + 1)
        self.client.logout()

    def test_retrieve_registration(self):
        """
        Ensure a users can retrieve doctor registration.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        registration = Registration.objects.create(
            doctor=doctor,
            registration="Registration-j",
            date=dt.date.today() - dt.timedelta(days=366),
        )

        url = reverse("doctor:registration-detail", args=(doctor.id, registration.id))

        # Test if unautheticated user cannot retrieve models
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("id", None), None)

        # Test if autheticated user can retrieve models
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], registration.id)
        self.client.logout()

    def test_update_registration(self):
        """
        Ensure a doctor can update Registration.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        registration = Registration.objects.create(
            doctor=doctor,
            registration="Registration-j",
            date=dt.date.today() - dt.timedelta(days=366),
        )

        url = reverse("doctor:registration-detail", args=(doctor.id, registration.id))

        data = {
            "doctor": doctor.id,
            "registration": "Registration X",
            "date": dt.date.today() - dt.timedelta(days=(366 * 2)),
        }

        # Test if unautheticated user can update
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(
            Registration.objects.get(id=registration.id).registration,
            data["registration"],
        )

        # Test if non-doctor user cannot update
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Registration.objects.get(id=registration.id).registration,
            data["registration"],
        )
        self.client.logout()

        # Test if non-owner doctor user cannot update
        user = create_user(name="d.user2", role="DOCTOR")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Registration.objects.get(id=registration.id).registration,
            data["registration"],
        )
        self.client.logout()

        # Test if owner doctor can create models
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Registration.objects.get(id=registration.id).registration,
            data["registration"],
        )
        self.client.logout()

    def test_delete_registration(self):
        """
        Ensure a doctor can delete their Registration.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        obj = Registration.objects.create(
            doctor=doctor,
            registration="Registration-j",
            date=dt.date.today() - dt.timedelta(days=366),
        )

        url = reverse("doctor:registration-detail", args=(doctor.id, obj.id))

        # Test if unautheticated user cannot delete
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Registration.objects.filter(id=obj.id).exists())

        # Test if non doctor user cannot delete
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Registration.objects.filter(id=obj.id).exists())
        self.client.logout()

        # Test if non owner doctor user cannot delete
        user = create_user(name="d.user2", role="DOCTOR")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Registration.objects.filter(id=obj.id).exists())
        self.client.logout()

        # Test if owner doctor can destroy
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Registration.objects.filter(id=obj.id).exists())
        self.client.logout()


class DoctorScheduleViewTests(APITestCase):
    def setUp(self):
        pass

    def test_list_doctors_schedule(self):
        """
        Ensure you can list doctors schedule.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        timeslot = TimeSlot.objects.create(
            doctor=doctor,
            start_time=dt.time(hour=9, minute=30),
            end_time=dt.time(hour=10, minute=30),
            number_of_appointments=1,
        )
        for day in DoctorSchedule.DAY:
            schedule = DoctorSchedule.objects.create(doctor=doctor, day=day[0])
            schedule.time_slot.add(timeslot)
            schedule.save()

        doctor2 = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        timeslot = TimeSlot.objects.create(
            doctor=doctor2,
            start_time=dt.time(hour=9, minute=30),
            end_time=dt.time(hour=10, minute=30),
            number_of_appointments=1,
        )
        for day in DoctorSchedule.DAY:
            schedule = DoctorSchedule.objects.create(doctor=doctor2, day=day[0])
            schedule.time_slot.add(timeslot)
            schedule.save()

        url = reverse("doctor:doctorschedule-list", args=(doctor.id,))

        # Test if unautheticated user cannot list models
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("results", None), None)

        # Test if autheticated user can list models
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.json()["results"]),
            DoctorSchedule.objects.filter(doctor=doctor.id).count(),
        )
        for data in response.json()["results"]:
            self.assertEqual(data["doctor"], doctor.id)
        self.client.logout()

    def test_create_doctors_schedule(self):
        """
        Ensure a doctor can add doctors_schedule.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        timeslot = TimeSlot.objects.create(
            doctor=doctor,
            start_time=dt.time(hour=9, minute=30),
            end_time=dt.time(hour=10, minute=30),
            number_of_appointments=1,
        )

        obj_data = {
            "doctor": doctor.id,
            "day": "Monday",
            "time_slot": [
                timeslot.id,
            ],
        }
        obj_count = DoctorSchedule.objects.count()

        url = reverse("doctor:doctorschedule-list", args=(doctor.id,))

        # Test if unautheticated user can create models
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(DoctorSchedule.objects.count(), obj_count)

        # Test if non-doctor user can create models
        user = create_user(role="PATIENT")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(DoctorSchedule.objects.count(), obj_count)
        self.client.logout()

        # Test if non-owner doctor can create models
        user = create_user(name="d.user2", role="DOCTOR")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(DoctorSchedule.objects.count(), obj_count)
        self.client.logout()

        # Test if owner doctor can create models
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DoctorSchedule.objects.count(), obj_count + 1)
        self.client.logout()

    def test_retrieve_doctors_schedule(self):
        """
        Ensure a users can retrieve doctor schedule.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        timeslot = TimeSlot.objects.create(
            doctor=doctor,
            start_time=dt.time(hour=9, minute=30),
            end_time=dt.time(hour=10, minute=30),
            number_of_appointments=1,
        )

        schedule = DoctorSchedule.objects.create(doctor=doctor, day="Monday")
        schedule.time_slot.add(timeslot)
        schedule.save()

        url = reverse("doctor:doctorschedule-detail", args=(doctor.id, schedule.id))

        # Test if unautheticated user cannot retrieve models
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("id", None), None)

        # Test if autheticated user can retrieve models
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], schedule.id)
        self.client.logout()

    def test_update_doctors_schedule(self):
        """
        Ensure a doctor can update DoctorSchedule.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        timeslot = TimeSlot.objects.create(
            doctor=doctor,
            start_time=dt.time(hour=9, minute=30),
            end_time=dt.time(hour=10, minute=30),
            number_of_appointments=1,
        )

        schedule = DoctorSchedule.objects.create(doctor=doctor, day="Monday")
        schedule.time_slot.add(timeslot)
        schedule.save()

        url = reverse("doctor:doctorschedule-detail", args=(doctor.id, schedule.id))

        data = {
            "doctor": doctor.id,
            "time_slot": [
                timeslot.id,
            ],
            "day": "Tuesday",
        }

        # Test if unautheticated user can update
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(DoctorSchedule.objects.get(id=schedule.id).day, data["day"])

        # Test if non-doctor user cannot update
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(DoctorSchedule.objects.get(id=schedule.id).day, data["day"])
        self.client.logout()

        # Test if non-owner doctor user cannot update
        user = create_user(name="d.user2", role="DOCTOR")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(DoctorSchedule.objects.get(id=schedule.id).day, data["day"])
        self.client.logout()

        # Test if owner doctor can create models
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(DoctorSchedule.objects.get(id=schedule.id).day, data["day"])
        self.client.logout()

    def test_delete_doctors_schedule(self):
        """
        Ensure a doctor can delete their DoctorSchedule.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        timeslot = TimeSlot.objects.create(
            doctor=doctor,
            start_time=dt.time(hour=9, minute=30),
            end_time=dt.time(hour=10, minute=30),
            number_of_appointments=1,
        )

        obj = DoctorSchedule.objects.create(doctor=doctor, day="Monday")
        obj.time_slot.add(timeslot)
        obj.save()

        url = reverse("doctor:doctorschedule-detail", args=(doctor.id, obj.id))

        # Test if unautheticated user cannot delete
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(DoctorSchedule.objects.filter(id=obj.id).exists())

        # Test if non doctor user cannot delete
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(DoctorSchedule.objects.filter(id=obj.id).exists())
        self.client.logout()

        # Test if non owner doctor user cannot delete
        user = create_user(name="d.user2", role="DOCTOR")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(DoctorSchedule.objects.filter(id=obj.id).exists())
        self.client.logout()

        # Test if owner doctor can destroy
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(DoctorSchedule.objects.filter(id=obj.id).exists())
        self.client.logout()


class TimeSlotViewTests(APITestCase):
    def setUp(self):
        pass

    def test_list_timeslots(self):
        """
        Ensure you can list doctors timeslots.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        for x in range(1, 4):
            TimeSlot.objects.create(
                doctor=doctor,
                start_time=dt.time(hour=9 + x, minute=30),
                end_time=dt.time(hour=10 + x, minute=30),
                number_of_appointments=1,
            )

        doctor2 = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        for x in range(1, 3):
            TimeSlot.objects.create(
                doctor=doctor2,
                start_time=dt.time(hour=9 + x, minute=30),
                end_time=dt.time(hour=10 + x, minute=30),
                number_of_appointments=1,
            )

        url = reverse("doctor:timeslot-list", args=(doctor.id,))

        # Test if unautheticated user cannot list models
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("results", None), None)

        # Test if autheticated user can list models
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.json()["results"]),
            TimeSlot.objects.filter(doctor=doctor.id).count(),
        )
        for data in response.json()["results"]:
            self.assertEqual(data["doctor"], doctor.id)
        self.client.logout()

    def test_create_timeslot(self):
        """
        Ensure a doctor can add timeslots.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        obj_data = {
            "doctor": doctor.id,
            "start_time": dt.time(hour=9, minute=30),
            "end_time": dt.time(hour=10, minute=30),
            "number_of_appointments": 1,
        }
        obj_count = TimeSlot.objects.count()

        url = reverse("doctor:timeslot-list", args=(doctor.id,))

        # Test if unautheticated user can create models
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(TimeSlot.objects.count(), obj_count)

        # Test if non-doctor user can create models
        user = create_user(role="PATIENT")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(TimeSlot.objects.count(), obj_count)
        self.client.logout()

        # Test if non-owner doctor can create models
        user = create_user(name="d.user2", role="DOCTOR")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(TimeSlot.objects.count(), obj_count)
        self.client.logout()

        # Test if owner doctor can create models
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TimeSlot.objects.count(), obj_count + 1)
        self.client.logout()

    def test_retrieve_timeslot(self):
        """
        Ensure a users can retrieve timeslot.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        timeslot = TimeSlot.objects.create(
            doctor=doctor,
            start_time=dt.time(hour=9, minute=30),
            end_time=dt.time(hour=10, minute=30),
            number_of_appointments=1,
        )

        url = reverse("doctor:timeslot-detail", args=(doctor.id, timeslot.id))

        # Test if unautheticated user cannot retrieve models
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("id", None), None)

        # Test if autheticated user can retrieve models
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], timeslot.id)
        self.client.logout()

    def test_update_timeslot(self):
        """
        Ensure a doctor can update timeslot.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        timeslot = TimeSlot.objects.create(
            doctor=doctor,
            start_time=dt.time(hour=9, minute=30),
            end_time=dt.time(hour=10, minute=30),
            number_of_appointments=1,
        )

        url = reverse("doctor:timeslot-detail", args=(doctor.id, timeslot.id))

        data = {
            "doctor": doctor.id,
            "start_time": dt.time(hour=11, minute=30),
            "end_time": dt.time(hour=12, minute=30),
            "number_of_appointments": 3,
        }

        # Test if unautheticated user can update
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(
            TimeSlot.objects.get(id=timeslot.id).number_of_appointments,
            data["number_of_appointments"],
        )

        # Test if non-doctor user cannot update
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            TimeSlot.objects.get(id=timeslot.id).number_of_appointments,
            data["number_of_appointments"],
        )
        self.client.logout()

        # Test if non-owner doctor user cannot update
        user = create_user(name="d.user2", role="DOCTOR")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            TimeSlot.objects.get(id=timeslot.id).number_of_appointments,
            data["number_of_appointments"],
        )
        self.client.logout()

        # Test if owner doctor can create models
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            TimeSlot.objects.get(id=timeslot.id).number_of_appointments,
            data["number_of_appointments"],
        )
        self.client.logout()

    def test_delete_timeslot(self):
        """
        Ensure a doctor can delete their timeslot.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        obj = TimeSlot.objects.create(
            doctor=doctor,
            start_time=dt.time(hour=9, minute=30),
            end_time=dt.time(hour=10, minute=30),
            number_of_appointments=1,
        )

        url = reverse("doctor:timeslot-detail", args=(doctor.id, obj.id))

        # Test if unautheticated user cannot delete
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(TimeSlot.objects.filter(id=obj.id).exists())

        # Test if non doctor user cannot delete
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(TimeSlot.objects.filter(id=obj.id).exists())
        self.client.logout()

        # Test if non owner doctor user cannot delete
        user = create_user(name="d.user2", role="DOCTOR")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(TimeSlot.objects.filter(id=obj.id).exists())
        self.client.logout()

        # Test if owner doctor can destroy
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TimeSlot.objects.filter(id=obj.id).exists())
        self.client.logout()


class SocialMediaViewTests(APITestCase):
    def setUp(self):
        pass

    def test_list_registration(self):
        """
        Ensure you can list doctors registrations.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        for x in range(1, 4):
            SocialMedia.objects.create(
                doctor=doctor,
                name=f"SocialMedia-{x}",
                url=f"http://socialmedia{x}.com/",
            )

        doctor2 = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        for x in range(1, 3):
            SocialMedia.objects.create(
                doctor=doctor2,
                name=f"SocialMedia-{x}",
                url=f"http://socialmedia{x}.com/",
            )

        url = reverse("doctor:socialmedia-list", args=(doctor.id,))

        # Test if unautheticated user cannot list models
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("results", None), None)

        # Test if autheticated user can list models
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.json()["results"]),
            SocialMedia.objects.filter(doctor=doctor.id).count(),
        )
        for data in response.json()["results"]:
            self.assertEqual(data["doctor"], doctor.id)
        self.client.logout()

    def test_create_socialmedia(self):
        """
        Ensure a doctor can add Socials Details.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        obj_data = {
            "doctor": doctor.id,
            "name": "SocialMedia-x",
            "url": "http://socialmediax.com/",
        }
        obj_count = SocialMedia.objects.count()

        url = reverse("doctor:socialmedia-list", args=(doctor.id,))

        # Test if unautheticated user can create models
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(SocialMedia.objects.count(), obj_count)

        # Test if non-doctor user can create models
        user = create_user(role="PATIENT")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(SocialMedia.objects.count(), obj_count)
        self.client.logout()

        # Test if non-owner doctor can create models
        user = create_user(name="d.user2", role="DOCTOR")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(SocialMedia.objects.count(), obj_count)
        self.client.logout()

        # Test if owner doctor can create models
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SocialMedia.objects.count(), obj_count + 1)
        self.client.logout()

    def test_retrieve_socialmedia(self):
        """
        Ensure a users can retrieve socialmedia.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        social = SocialMedia.objects.create(
            doctor=doctor, name="SocialMedia-x", url="http://socialmediax.com/"
        )

        url = reverse("doctor:socialmedia-detail", args=(doctor.id, social.id))

        # Test if unautheticated user cannot retrieve models
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("id", None), None)

        # Test if autheticated user can retrieve models
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], social.id)
        self.client.logout()

    def test_update_socialmedia(self):
        """
        Ensure a doctor can update socialmedia.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        social = SocialMedia.objects.create(
            doctor=doctor, name="SocialMedia-x", url="http://socialmediax.com/"
        )

        url = reverse("doctor:socialmedia-detail", args=(doctor.id, social.id))

        data = {
            "doctor": doctor.id,
            "name": "MySocialMedia",
            "url": "http://mysocialmedia.com/",
        }

        # Test if unautheticated user can update
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(SocialMedia.objects.get(id=social.id).name, data["name"])

        # Test if non-doctor user cannot update
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(SocialMedia.objects.get(id=social.id).name, data["name"])
        self.client.logout()

        # Test if non-owner doctor user cannot update
        user = create_user(name="d.user2", role="DOCTOR")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(SocialMedia.objects.get(id=social.id).name, data["name"])
        self.client.logout()

        # Test if owner doctor can create models
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(SocialMedia.objects.get(id=social.id).name, data["name"])
        self.client.logout()

    def test_delete_socialmedia(self):
        """
        Ensure a doctor can delete their socialmedia.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        obj = SocialMedia.objects.create(
            doctor=doctor, name="SocialMedia-x", url="http://socialmediax.com/"
        )

        url = reverse("doctor:socialmedia-detail", args=(doctor.id, obj.id))

        # Test if unautheticated user cannot delete
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(SocialMedia.objects.filter(id=obj.id).exists())

        # Test if non doctor user cannot delete
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(SocialMedia.objects.filter(id=obj.id).exists())
        self.client.logout()

        # Test if non owner doctor user cannot delete
        user = create_user(name="d.user2", role="DOCTOR")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(SocialMedia.objects.filter(id=obj.id).exists())
        self.client.logout()

        # Test if owner doctor can destroy
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(SocialMedia.objects.filter(id=obj.id).exists())
        self.client.logout()


class AppointmentViewTests(APITestCase):
    def setUp(self):
        pass

    def test_list_appointment(self):
        """
        Ensure doctors can list their Appointments.
        """
        patient = Patient.objects.get_or_create(user=create_user(name="patient1"))[0]
        doctor2 = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date_of_appointment=timezone.make_aware(
                dt.datetime.utcnow() + dt.timedelta(days=7)
            ),
            purpose="tooth replacement",
            status="CONFIRMED",
        )
        Appointment.objects.create(
            patient=patient,
            doctor=doctor2,
            date_of_appointment=timezone.make_aware(
                dt.datetime.utcnow() + dt.timedelta(days=5)
            ),
            purpose="tooth replacement",
            status="CONFIRMED",
        )

        url = reverse("doctor:appointment-list", args=(doctor.id,))

        # check Doctor user can list their appointment-list
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.json()["results"]),
            Appointment.objects.filter(doctor=doctor.id).count(),
        )
        for data in response.json()["results"]:
            self.assertEqual(data["doctor"], doctor.id)
        self.client.logout()

        # check patient cannot list docs appointment-list
        self.client.login(username=patient.user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get("results", None), None)
        self.client.logout()

        # check if Doctor cannot get other doctors appointment-list
        self.client.login(username=doctor2.user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get("results", None), None)
        self.client.logout()

        # check if AnonymousUser will not return appointment-list
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("results", None), None)

    def test_create_appointment(self):
        """
        Ensure a doctor/patient can create appointment.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        # Add schedule to doctor
        timeslot = TimeSlot.objects.create(
            doctor=doctor,
            start_time=dt.time(hour=9, minute=30),
            end_time=dt.time(hour=10, minute=30),
            number_of_appointments=3,
        )
        for day in DoctorSchedule.DAY:
            schedule = DoctorSchedule.objects.create(doctor=doctor, day=day[0])
            schedule.time_slot.add(timeslot)
            schedule.save()

        # Test if owner cannot create appointment if unavailable appointment date
        d_o_a = dt.datetime(
            (dt.date.today() + dt.timedelta(days=7)).year,
            (dt.date.today() + dt.timedelta(days=7)).month,
            (dt.date.today() + dt.timedelta(days=7)).day,
            timeslot.start_time.hour,
            timeslot.start_time.minute,
        )

        patient = Patient.objects.create(user=create_user())

        obj_data = {
            "doctor": doctor.id,
            "patient": patient.id,
            "date_of_appointment": timezone.make_aware(d_o_a),
            "purpose": "tooth replacement",
        }
        obj_count = Appointment.objects.count()

        url = reverse("doctor:appointment-list", args=(doctor.id,))

        # Test if unautheticated user can create models
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Appointment.objects.count(), obj_count)

        # Test if patient can create models
        self.client.login(username=patient.user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        print(f"\n[------- create Appointments: {response.json()} ---------]\n")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), obj_count + 1)
        self.client.logout()

        # Test if non-owner doctor can create models
        doctor1 = Doctor.objects.create(
            user=create_user(name="d.user2", role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        self.client.login(username=doctor1.user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Appointment.objects.count(), obj_count + 1)
        self.client.logout()

        # Test if owner doctor can create models
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), obj_count + 2)
        self.client.logout()

    def test_retrieve_appointment(self):
        """
        Ensure a doctor can retrieve Appointments.
        """
        patient = Patient.objects.get_or_create(user=create_user(name="patient1"))[0]
        doctor2 = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date_of_appointment=timezone.make_aware(
                dt.datetime.utcnow() + dt.timedelta(days=7)
            ),
            purpose="tooth replacement",
            status="CONFIRMED",
        )

        url = reverse("doctor:appointment-detail", args=(doctor.id, appointment.id))

        # Test if unautheticated user cannot retrieve models
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("id", None), None)

        # Test if non owner doc cannot retrieve models
        self.client.login(username=doctor2.user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get("id", None), None)
        self.client.logout()

        # Test if patient cannot retrieve models
        self.client.login(username=patient.user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get("id", None), None)
        self.client.logout()

        # Test if autheticated owner doctor can retrieve models
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], appointment.id)
        self.client.logout()

    def test_update_appointment(self):
        """
        Ensure NO user can update appointment.
        """
        patient = Patient.objects.get_or_create(user=create_user(name="patient1"))[0]
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date_of_appointment=timezone.make_aware(
                dt.datetime.utcnow() - dt.timedelta(days=7)
            ),
            purpose="tooth replacement",
            status="WAITING",
        )

        url = reverse("doctor:appointment-detail", args=(doctor.id, appointment.id))

        data = {
            "status": "CONFIRMED",
            "purpose": "Tooth Surgery",
            "date_of_appointment": timezone.make_aware(
                dt.datetime.utcnow() - dt.timedelta(days=5)
            ),
        }

        # Test if unautheticated user can update
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(
            Appointment.objects.get(id=appointment.id).status, data["status"]
        )

        # Test if non-doctor user cannot update
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Appointment.objects.get(id=appointment.id).status, data["status"]
        )
        self.client.logout()

        # Test if non-owner doctor user cannot update
        user = create_user(name="d.user2", role="DOCTOR")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Appointment.objects.get(id=appointment.id).status, data["status"]
        )
        self.client.logout()

        # Test if owner doctor cannot update models
        self.client.login(
            username=appointment.doctor.user.username, password="Pass1234"
        )
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertNotEqual(
            Appointment.objects.get(id=appointment.id).status, data["status"]
        )
        self.client.logout()

        # Test if owner patient cannot update models
        self.client.login(
            username=appointment.patient.user.username, password="Pass1234"
        )
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Appointment.objects.get(id=appointment.id).status, data["status"]
        )
        self.client.logout()

    def test_delete_appointment(self):
        """
        Ensure a users cannot delete appointment.
        """
        patient = Patient.objects.get_or_create(user=create_user(name="patient1"))[0]
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date_of_appointment=timezone.make_aware(
                dt.datetime.utcnow() - dt.timedelta(days=7)
            ),
            purpose="tooth replacement",
            status="WAITING",
        )

        url = reverse("doctor:appointment-detail", args=(doctor.id, appointment.id))

        # Test if unautheticated user cannot delete
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Appointment.objects.filter(id=appointment.id).exists())

        # Test if non-doctor user cannot delete
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Appointment.objects.filter(id=appointment.id).exists())
        self.client.logout()

        # Test if non-owner doctor user cannot delete
        user = create_user(name="d.user2", role="DOCTOR")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Appointment.objects.filter(id=appointment.id).exists())
        self.client.logout()

        # Test if owner doctor cannot delete models
        self.client.login(
            username=appointment.doctor.user.username, password="Pass1234"
        )
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertTrue(Appointment.objects.filter(id=appointment.id).exists())
        self.client.logout()

        # Test if owner patient cannot delete models
        self.client.login(
            username=appointment.patient.user.username, password="Pass1234"
        )
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Appointment.objects.filter(id=appointment.id).exists())
        self.client.logout()

    def test_update_appointment_status(self):
        """
        Ensure doctor can update appointment status.
        """
        patient = Patient.objects.get_or_create(user=create_user(name="patient1"))[0]
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date_of_appointment=timezone.make_aware(
                dt.datetime.utcnow() - dt.timedelta(days=7)
            ),
            purpose="tooth replacement",
            status="WAITING",
        )

        url = reverse(
            "doctor:appointment-update-status", args=(doctor.id, appointment.id)
        )

        data = {
            "status": "CONFIRMED",
        }

        # Test if unautheticated user can update
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(
            Appointment.objects.get(id=appointment.id).status, data["status"]
        )

        # Test if non-doctor user cannot update
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Appointment.objects.get(id=appointment.id).status, data["status"]
        )
        self.client.logout()

        # Test if non-owner doctor user cannot update
        user = create_user(name="d.user2", role="DOCTOR")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Appointment.objects.get(id=appointment.id).status, data["status"]
        )
        self.client.logout()

        # Test if owner patient can update models
        self.client.login(
            username=appointment.patient.user.username, password="Pass1234"
        )
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Appointment.objects.get(id=appointment.id).status, data["status"]
        )
        self.client.logout()

        # Test if owner doctor can update models status only
        self.client.login(
            username=appointment.doctor.user.username, password="Pass1234"
        )
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_obj = Appointment.objects.get(id=appointment.id)
        self.assertEqual(updated_obj.status, data["status"])
        self.client.logout()

    def test_cancel_appointment(self):
        """
        Ensure a users can cancel appointment.
        - Doc can cancel appointment
        - Pat can cancel appointment
        """
        patient = Patient.objects.get_or_create(user=create_user(name="patient1"))[0]
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date_of_appointment=timezone.make_aware(
                dt.datetime.utcnow() - dt.timedelta(days=7)
            ),
            purpose="tooth replacement",
            status="WAITING",
        )

        url = reverse("doctor:appointment-cancel", args=(doctor.id, appointment.id))

        # Test if unautheticated user can update
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(
            Appointment.objects.get(id=appointment.id).status, "CANCELED"
        )

        # Test if non-doctor user cannot cancel appointment
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Appointment.objects.get(id=appointment.id).status, "CANCELED"
        )
        self.client.logout()

        # Test if non-owner doctor user cannot cancel appointment
        user = create_user(name="d.user2", role="DOCTOR")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Appointment.objects.get(id=appointment.id).status, "CANCELED"
        )
        self.client.logout()

        # Test if owner patient cannot cancel appointment
        self.client.login(
            username=appointment.patient.user.username, password="Pass1234"
        )
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Appointment.objects.get(id=appointment.id).status, "CANCELED"
        )
        self.client.logout()

        # Test if owner doctor can cancel appointment
        self.client.login(
            username=appointment.doctor.user.username, password="Pass1234"
        )
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Appointment.objects.get(id=appointment.id).status, "CANCELED")
        self.client.logout()


class AppoinmentReviewViewTests(APITestCase):
    def setUp(self):
        pass

    def test_list_appointment_reviews(self):
        """
        Ensure users can list their Appointment Reviews.
        """
        patient = Patient.objects.get_or_create(user=create_user())[0]
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date_of_appointment=timezone.make_aware(
                dt.datetime.utcnow() - dt.timedelta(days=7)
            ),
            purpose="tooth replacement",
            status="COMPLETED",
        )
        AppoinmentReview.objects.create(
            appointment=appointment,
            rate=4,
            recommend=True,
            text="Kindly and Well Served!!",
        )

        doctor2 = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor2,
            date_of_appointment=timezone.make_aware(
                dt.datetime.utcnow() - dt.timedelta(days=5)
            ),
            purpose="tooth replacement",
            status="COMPLETED",
        )
        AppoinmentReview.objects.create(
            appointment=appointment,
            rate=4,
            recommend=True,
            text="Kindly and Well Served!!",
        )

        url = reverse("doctor:appoinmentreview-list", args=(doctor.id,))

        # Test if unautheticated user cannot list models
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("results", None), None)

        # Test if autheticated user can list models
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.json()["results"]),
            AppoinmentReview.objects.filter(appointment__doctor=doctor.id).count(),
        )
        for data in response.json()["results"]:
            appointment_id = data["appointment"]
            self.assertEqual(
                Appointment.objects.get(id=appointment_id).doctor.id, doctor.id
            )
        self.client.logout()

    def test_create_appointment_reviews(self):
        """
        Ensure a doctor/patient can create appointment reviews.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        patient = Patient.objects.get_or_create(user=create_user())[0]
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date_of_appointment=timezone.make_aware(
                dt.datetime.utcnow() - dt.timedelta(days=7)
            ),
            purpose="tooth replacement",
            status="COMPLETED",
        )

        obj_data = {
            "appointment": appointment.id,
            "rate": 4,
            "recommend": True,
            "text": "Kindly and Well Served!!",
        }
        obj_count = AppoinmentReview.objects.count()

        url = reverse("doctor:appoinmentreview-list", args=(doctor.id,))

        # Test if unautheticated user can create models
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(AppoinmentReview.objects.count(), obj_count)

        # Test if owner doctor user cannot create models
        user = create_user(role="PATIENT")
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(AppoinmentReview.objects.count(), obj_count)
        self.client.logout()

        # Test if non-owner doctor cannot create models
        user = create_user(name="d.user2", role="DOCTOR")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(AppoinmentReview.objects.count(), obj_count)
        self.client.logout()

        # Test if patient can create models
        self.client.login(username=patient.user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AppoinmentReview.objects.count(), obj_count + 1)
        self.client.logout()

    def test_retrieve_appointment_reviews(self):
        """
        Ensure a users can retrieve Appointment-Reviews.
        """
        patient = Patient.objects.get_or_create(user=create_user(name="patient1"))[0]
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date_of_appointment=timezone.make_aware(
                dt.datetime.utcnow() - dt.timedelta(days=7)
            ),
            purpose="tooth replacement",
            status="COMPLETED",
        )
        review = AppoinmentReview.objects.create(
            appointment=appointment,
            rate=4,
            recommend=True,
            text="Kindly and Well Served!!",
        )

        url = reverse("doctor:appoinmentreview-detail", args=(doctor.id, review.id))

        # Test if unautheticated user cannot retrieve models
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("id", None), None)

        # Test if autheticated user can retrieve models
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], review.id)
        self.client.logout()

    def test_update_appoinment_reviews(self):
        """
        Ensure a doctor can update Appointment-Reviews.
        """
        patient = Patient.objects.get_or_create(user=create_user(name="patient1"))[0]
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date_of_appointment=timezone.make_aware(
                dt.datetime.utcnow() - dt.timedelta(days=7)
            ),
            purpose="tooth replacement",
            status="COMPLETED",
        )
        review = AppoinmentReview.objects.create(
            appointment=appointment,
            rate=4,
            recommend=True,
            text="Kindly and Well Served!!",
        )

        url = reverse("doctor:appoinmentreview-detail", args=(doctor.id, review.id))

        data = {
            "appointment": appointment.id,
            "rate": 5,
            "recommend": True,
            "text": "Excellent Service!!",
        }

        # Test if unautheticated user can update
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(
            AppoinmentReview.objects.get(id=review.id).text, data["text"]
        )

        # Test if non-doctor user cannot update
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            AppoinmentReview.objects.get(id=review.id).text, data["text"]
        )
        self.client.logout()

        # Test if non-owner doctor user cannot update
        user = create_user(name="d.user2", role="DOCTOR")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            AppoinmentReview.objects.get(id=review.id).text, data["text"]
        )
        self.client.logout()

        # Test if owner doctor cannot update models
        self.client.login(
            username=review.appointment.doctor.user.username, password="Pass1234"
        )
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            AppoinmentReview.objects.get(id=review.id).text, data["text"]
        )
        self.client.logout()

        # Test if owner patient can update models
        self.client.login(
            username=review.appointment.patient.user.username, password="Pass1234"
        )
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(AppoinmentReview.objects.get(id=review.id).text, data["text"])
        self.client.logout()

    def test_delete_appointment_reviews(self):
        """
        Ensure a doctor can delete their Appointment-Reviews.
        """
        patient = Patient.objects.get_or_create(user=create_user())[0]
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date_of_appointment=timezone.make_aware(
                dt.datetime.utcnow() - dt.timedelta(days=7)
            ),
            purpose="tooth replacement",
            status="COMPLETED",
        )
        obj = AppoinmentReview.objects.create(
            appointment=appointment,
            rate=4,
            recommend=True,
            text="Kindly and Well Served!!",
        )

        url = reverse("doctor:appoinmentreview-detail", args=(doctor.id, obj.id))

        # Test if unautheticated user cannot delete
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(AppoinmentReview.objects.filter(id=obj.id).exists())

        # Test if non doctor user cannot delete
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(AppoinmentReview.objects.filter(id=obj.id).exists())
        self.client.logout()

        # Test if non owner doctor user cannot delete
        user = create_user(name="d.user2", role="DOCTOR")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(AppoinmentReview.objects.filter(id=obj.id).exists())
        self.client.logout()

        # Test if owner doctor cannot destroy
        self.client.login(
            username=obj.appointment.doctor.user.username, password="Pass1234"
        )
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(AppoinmentReview.objects.filter(id=obj.id).exists())
        self.client.logout()

        # Test if owner patient can delete
        self.client.login(
            username=obj.appointment.patient.user.username, password="Pass1234"
        )
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(AppoinmentReview.objects.filter(id=obj.id).exists())
        self.client.logout()

    def test_review_reaction(self):
        """
        Ensure a user can recommend/unrecommend Appointment-Reviews.
        """
        patient = Patient.objects.get_or_create(user=create_user())[0]
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date_of_appointment=timezone.make_aware(
                dt.datetime.utcnow() - dt.timedelta(days=7)
            ),
            purpose="tooth replacement",
            status="COMPLETED",
        )
        obj = AppoinmentReview.objects.create(
            appointment=appointment,
            rate=4,
            recommend=True,
            text="Kindly and Well Served!!",
        )

        url = reverse("doctor:appoinmentreview-react", args=(doctor.id, obj.id))

        obj_data = {"review": obj.id, "recommend": True}

        obj_count = LikedReview.objects.count()

        # Test if unautheticated user can create models
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(LikedReview.objects.count(), obj_count)

        # Test if user can recommend review
        user = create_user(role="PATIENT")
        obj_data.update({"user": user.id})
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        print(f"\n[------- like review: {response.json()} ---------]\n")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LikedReview.objects.count(), obj_count + 1)
        self.assertTrue(LikedReview.objects.last().recommend)
        self.client.logout()

        # Test if user can dislike review
        user = create_user(name="d.user2", role="DOCTOR")
        obj_data = {"review": obj.id, "recommend": False, "user": user.id}
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LikedReview.objects.count(), obj_count + 2)
        self.assertFalse(LikedReview.objects.last().recommend)
        self.client.logout()

    def test_delete_review_reaction(self):
        """
        Ensure a user can delete their recommend/unrecommend Appointment-Reviews.
        """
        patient = Patient.objects.get_or_create(user=create_user())[0]
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date_of_appointment=timezone.make_aware(
                dt.datetime.utcnow() - dt.timedelta(days=7)
            ),
            purpose="tooth replacement",
            status="COMPLETED",
        )
        obj = AppoinmentReview.objects.create(
            appointment=appointment,
            rate=4,
            recommend=True,
            text="Kindly and Well Served!!",
        )

        url = reverse("doctor:appoinmentreview-react", args=(doctor.id, obj.id))

        user = create_user()
        like = LikedReview.objects.create(user=user, review=obj, recommend=True)

        # Test if unautheticated user can create models
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(LikedReview.objects.filter(id=like.id).exists())

        # Test if owner user can recommend review
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(LikedReview.objects.filter(id=like.id).exists())
        self.client.logout()


class ReviewReplyViewTests(APITestCase):
    def setUp(self):
        pass

    def test_list_review_replies(self):
        """
        Ensure users can list Replies.
        """
        patient = Patient.objects.get_or_create(user=create_user())[0]
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date_of_appointment=timezone.make_aware(
                dt.datetime.utcnow() - dt.timedelta(days=7)
            ),
            purpose="tooth replacement",
            status="COMPLETED",
        )
        review = AppoinmentReview.objects.create(
            appointment=appointment,
            rate=4,
            recommend=True,
            text="Me too, Kindly and Well Served!!",
        )

        Reply.objects.create(
            user=create_user(),
            review=review,
            text="Kindly and Well Served!!",
        )

        Reply.objects.create(
            user=create_user(name="Wolves"),
            review=review,
            text="Review helped",
        )

        url = reverse("doctor:reply-list", args=(doctor.id, review.id))

        # Test if unautheticated user cannot list models
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("results", None), None)

        # Test if autheticated user can list models
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.json()["results"]),
            Reply.objects.filter(review=review.id).count(),
        )
        self.client.logout()

    def test_create_review_replies(self):
        """
        Ensure a users can reply appointment reviews.
        """
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        patient = Patient.objects.get_or_create(user=create_user())[0]
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date_of_appointment=timezone.make_aware(
                dt.datetime.utcnow() - dt.timedelta(days=7)
            ),
            purpose="tooth replacement",
            status="COMPLETED",
        )
        review = AppoinmentReview.objects.create(
            appointment=appointment,
            rate=4,
            recommend=True,
            text="Me too, Kindly and Well Served!!",
        )

        obj_data = {
            "review": review.id,
            "text": "Kindly and Well Served!!",
        }
        obj_count = Reply.objects.count()

        url = reverse("doctor:reply-list", args=(doctor.id, review.id))

        # Test if unautheticated user can create models
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Reply.objects.count(), obj_count)

        # Test if owner doctor user cannot create models
        user = create_user(role="PATIENT")
        obj_data.update({"user": user.id})
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reply.objects.count(), obj_count + 1)
        self.client.logout()

    def test_retrieve_review_replies(self):
        """
        Ensure a users can retrieve Replies.
        """
        patient = Patient.objects.get_or_create(user=create_user())[0]
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date_of_appointment=timezone.make_aware(
                dt.datetime.utcnow() - dt.timedelta(days=7)
            ),
            purpose="tooth replacement",
            status="COMPLETED",
        )
        review = AppoinmentReview.objects.create(
            appointment=appointment,
            rate=4,
            recommend=True,
            text="Me too, Kindly and Well Served!!",
        )

        reply = Reply.objects.create(
            user=create_user(),
            review=review,
            text="Kindly and Well Served!!",
        )

        url = reverse("doctor:reply-detail", args=(doctor.id, review.id, reply.id))

        # Test if unautheticated user cannot retrieve models
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("id", None), None)

        # Test if autheticated user can retrieve models
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], reply.id)
        self.client.logout()

    def test_update_appoinment_reviews(self):
        """
        Ensure a doctor can update Appointment-Reviews.
        """
        patient = Patient.objects.get_or_create(user=create_user())[0]
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date_of_appointment=timezone.make_aware(
                dt.datetime.utcnow() - dt.timedelta(days=7)
            ),
            purpose="tooth replacement",
            status="COMPLETED",
        )
        review = AppoinmentReview.objects.create(
            appointment=appointment,
            rate=4,
            recommend=True,
            text="Me too, Kindly and Well Served!!",
        )

        user = create_user()

        reply = Reply.objects.create(
            user=user,
            review=review,
            text="Kindly and Well Served!!",
        )

        url = reverse("doctor:reply-detail", args=(doctor.id, review.id, reply.id))

        data = {
            "user": user.id,
            "review": review.id,
            "text": "Truly, Excellent Service!!",
        }

        # Test if unautheticated user can update
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(Reply.objects.get(id=reply.id).text, data["text"])

        # Test if non-owner user cannot update
        user1 = create_user()
        self.client.login(username=user1.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(Reply.objects.get(id=reply.id).text, data["text"])
        self.client.logout()

        # Test if owner patient can update models
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Reply.objects.get(id=reply.id).text, data["text"])
        self.client.logout()

    def test_delete_review_replies(self):
        """
        Ensure a doctor can delete their Reviews Replies.
        """
        patient = Patient.objects.get_or_create(user=create_user())[0]
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date_of_appointment=timezone.make_aware(
                dt.datetime.utcnow() - dt.timedelta(days=7)
            ),
            purpose="tooth replacement",
            status="COMPLETED",
        )
        review = AppoinmentReview.objects.create(
            appointment=appointment,
            rate=4,
            recommend=True,
            text="Kindly and Well Served!!",
        )

        user = create_user()

        obj = Reply.objects.create(
            user=user,
            review=review,
            text="Kindly and Well Served!!",
        )

        url = reverse("doctor:reply-detail", args=(doctor.id, review.id, obj.id))

        # Test if unautheticated user cannot delete
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Reply.objects.filter(id=obj.id).exists())

        # Test if owner user can delete
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Reply.objects.filter(id=obj.id).exists())
        self.client.logout()

    def test_reply_reaction(self):
        """
        Ensure a user can recommend/unrecommend Replies.
        """
        patient = Patient.objects.get_or_create(user=create_user())[0]
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date_of_appointment=timezone.make_aware(
                dt.datetime.utcnow() - dt.timedelta(days=7)
            ),
            purpose="tooth replacement",
            status="COMPLETED",
        )
        review = AppoinmentReview.objects.create(
            appointment=appointment,
            rate=4,
            recommend=True,
            text="Kindly and Well Served!!",
        )

        obj = Reply.objects.create(
            user=create_user(),
            review=review,
            text="Kindly and Well Served!!",
        )

        url = reverse("doctor:reply-react", args=(doctor.id, review.id, obj.id))

        obj_data = {"reply": obj.id, "recommend": True}

        obj_count = LikedReply.objects.count()

        # Test if unautheticated user can create models
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(LikedReply.objects.count(), obj_count)

        # Test if user can recommend review
        user = create_user(role="PATIENT")
        obj_data.update({"user": user.id})
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LikedReply.objects.count(), obj_count + 1)
        self.assertTrue(LikedReply.objects.last().recommend)
        self.client.logout()

        # Test if user can dislike reply
        user = create_user(name="d.user2", role="DOCTOR")
        obj_data = {"reply": obj.id, "recommend": False, "user": user.id}
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.post(url, obj_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LikedReply.objects.count(), obj_count + 2)
        self.assertFalse(LikedReply.objects.last().recommend)
        self.client.logout()

    def test_delete_reply_reaction(self):
        """
        Ensure a user can delete their recommend/unrecommend Replies.
        """
        patient = Patient.objects.get_or_create(user=create_user())[0]
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date_of_appointment=timezone.make_aware(
                dt.datetime.utcnow() - dt.timedelta(days=7)
            ),
            purpose="tooth replacement",
            status="COMPLETED",
        )
        review = AppoinmentReview.objects.create(
            appointment=appointment,
            rate=4,
            recommend=True,
            text="Kindly and Well Served!!",
        )

        user = create_user()

        reply = Reply.objects.create(
            user=user,
            review=review,
            text="Kindly and Well Served!!",
        )

        obj = LikedReply.objects.create(reply=reply, user=user, recommend=True)

        url = reverse("doctor:reply-react", args=(doctor.id, review.id, reply.id))

        # Test if unautheticated user can create models
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(LikedReply.objects.filter(id=obj.id).exists())

        # Test if owner user can recommend review
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(LikedReply.objects.filter(id=obj.id).exists())
        self.client.logout()
