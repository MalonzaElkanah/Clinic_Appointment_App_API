from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from client.models import MyUser
from clinic.models import Clinic, Doctor
from administrator.models import Speciality
from clinic.tests.utils import create_default_doctor, create_user

from mylib import token


class ListCreateRetrieveUpdateDestroyClinicViewTests(APITestCase):
    def setUp(self):
        """
        Create user and Clinic Object to be used
        through-out this Clinic Tests Case.
        """
        Clinic.objects.get_or_create(
            user=create_user(),
            name="test clinic",
            phone="0798976234",
            email="tvirus@myapp.com",
        )

    def test_list_clinic(self):
        """
        Ensure authenticated user can list clinics.
        """
        url = reverse("clinic_list_create")

        # Test if unautheticated user cannot list
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("results", None), None)

        # Test if non-admin user can list
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), Clinic.objects.count())
        self.client.logout()

    def test_create_clinic(self):
        """
        Ensure authenticated user can create clinic.
        """
        url = reverse("clinic_list_create")
        data = {
            "name": "clinic101",
            "phone": "0712345678",
            "email": "clinic101@myapp.com",
        }
        clinic_count = Clinic.objects.count()

        # Test if unauthenticated user cannot create clinic
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Clinic.objects.count(), clinic_count)

        # Test if authenticated user can create clinic
        user = create_default_doctor()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Clinic.objects.count(), clinic_count + 1)
        self.assertEqual(Clinic.objects.last().name, data["name"])
        self.client.logout()

    def test_retrieve_clinic(self):
        """
        Ensure authenticated clinic owner can retrieve their clinic.
        """
        user = create_user()
        clinic = Clinic.objects.get_or_create(
            user=user, name="my clinic", phone="0718976234", email="myclinic@myapp.com"
        )[0]
        url = reverse("clinic_retrieve_update", args=(clinic.id,))

        # Test if unautheticated user cannot retrieve
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("results", None), None)

        # Test if non-admin user can retrieve
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["name"], clinic.name)
        self.client.logout()

    def test_update_clinic(self):
        """
        Ensure authenticated clinic owner can update their clinic.
        """
        user = create_user()
        clinic = Clinic.objects.get_or_create(
            user=user, name="my clinic", phone="0718976234", email="myclinic@myapp.com"
        )[0]
        url = reverse("clinic_retrieve_update", args=(clinic.id,))
        data = {
            "name": "just clinic",
            "phone": "0711345678",
            "email": "myclinic@myapp.com",
        }

        # Test if unautheticated user can update
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(Clinic.objects.get(id=clinic.id).name, "just clinic")

        # Test if non-owner user can update
        user1 = create_user()
        self.client.login(username=user1.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(Clinic.objects.get(id=clinic.id).name, "just clinic")
        self.client.logout()

        # Test if owner user user can update
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Clinic.objects.get(id=clinic.id).name, "just clinic")
        self.client.logout()

    def test_destroy_clinic(self):
        """
        Ensure authenticated clinic owner can delete their clinic.
        """
        user = create_user()
        clinic = Clinic.objects.get_or_create(
            user=user, name="my clinic", phone="0718976234", email="myclinic@myapp.com"
        )[0]
        url = reverse("clinic_retrieve_update", args=(clinic.id,))

        # Test if unautheticated user can delete
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Clinic.objects.filter(id=clinic.id).exists())

        # Test if non-owner user can delete
        user1 = create_user()
        self.client.login(username=user1.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Clinic.objects.filter(id=clinic.id).exists())
        self.client.logout()

        # Test if owner can delete
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Clinic.objects.filter(id=clinic.id).exists())
        self.client.logout()


class ClinicInviteDoctorViewTests(APITestCase):
    def setUp(self):
        """
        Create user and Clinic Object to be used
        through-out this Clinic Tests Case.
        """
        Doctor.objects.get_or_create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="dentist")[0],
        )

    def test_clinic_invite_doctor(self):
        """
        Ensure authenticated clinic owner can invite doctor to their clinic.
        """
        user = create_user()
        clinic = Clinic.objects.get_or_create(
            user=user, name="my clinic", phone="0718976234", email="myclinic@myapp.com"
        )[0]
        url = reverse("clinic_invite_doctor", args=(clinic.id,))
        data = {"doctor_email": "user3@myapp.com", "doctor_phone_number": "0712345671"}

        # Test if unautheticated user cannot create an invite
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        if MyUser.objects.filter(email=data["doctor_email"]).exists():
            doctor = Doctor.objects.filter(
                user=MyUser.objects.filter(email=data["doctor_email"])[0]
            )

            if doctor.exists():
                self.assertNotIn(clinic, doctor[0].clinic_invites)

        # Test if non-owner user cannot create invite
        user1 = create_user()
        self.client.login(username=user1.username, password="Pass1234")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        if MyUser.objects.filter(email=data["doctor_email"]).exists():
            doctor = Doctor.objects.filter(
                user=MyUser.objects.filter(email=data["doctor_email"])[0]
            )

            if doctor.exists():
                self.assertNotIn(clinic, doctor[0].clinic_invites)
        self.client.logout()

        # Test if clinic owner can invite a new doctor
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if MyUser.objects.filter(email=data["doctor_email"]).exists():
            doctor = Doctor.objects.filter(
                user=MyUser.objects.filter(email=data["doctor_email"])[0]
            )

            if doctor.exists():
                self.assertIn(clinic, list(doctor[0].clinic_invites.all()))

        # Test if clinic owner can Invite exisiting doctor
        doctor = Doctor.objects.get_or_create(
            user=create_default_doctor(),
            speciality=Speciality.objects.get_or_create(name="dentist")[0],
        )[0]
        data = {
            "doctor_email": doctor.user.email,
            "doctor_phone_number": doctor.user.phone,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(clinic, list(doctor.clinic_invites.all()))
        self.client.logout()


class DoctorAcceptRejectInviteViewTests(APITestCase):
    def setUp(self):
        """
        Create user and Clinic Object to be used
        through-out this Clinic Tests Case.
        """
        pass

    def test_doctor_accept_clinic_invite(self):
        """
        Ensure invited doctor can accept clinic invite.
        """
        user = create_user()
        clinic = Clinic.objects.get_or_create(
            user=user, name="my clinic", phone="0718976234", email="myclinic@myapp.com"
        )[0]

        doctor = Doctor.objects.get_or_create(
            user=create_default_doctor(),
            speciality=Speciality.objects.get_or_create(name="dentist")[0],
        )[0]
        doctor.clinic_invites.add(clinic)
        doctor.save()

        str_token = token.encode(
            doctor.user.email, expiration_seconds=(60 * 60 * 24 * 7)
        )

        url = f"{reverse('doctor_accept_invite', args=(clinic.id,))}?token={str_token}"
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json()["detail"],
            "Invite Accepted. Please login to finish setting your doctor profile.",
        )
        self.assertIn(doctor, list(clinic.doctors.all()))

        # Test new user invite
        user = MyUser.objects.create(phone="0716976234", email="newuser@myapp.com")
        doctor = Doctor.objects.get_or_create(
            user=user, speciality=Speciality.objects.get_or_create(name="dentist")[0]
        )[0]
        doctor.clinic_invites.add(clinic)
        doctor.save()

        str_token = token.encode(
            doctor.user.email, expiration_seconds=(60 * 60 * 24 * 7)
        )

        url = f"{reverse('doctor_accept_invite', args=(clinic.id,))}?token={str_token}"
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json()["detail"],
            "Invite Accepted. Code to setup your account has been sent to your email.",
        )
        self.assertIn(doctor, list(clinic.doctors.all()))

        # Test bad token invite
        doctor = Doctor.objects.get_or_create(
            user=create_default_doctor(),
            speciality=Speciality.objects.get_or_create(name="dentist")[0],
        )[0]
        doctor.clinic_invites.add(clinic)
        doctor.save()

        str_token = token.encode(
            doctor.user.phone, expiration_seconds=(60 * 60 * 24 * 7)
        )

        url = f"{reverse('doctor_accept_invite', args=(clinic.id,))}?token={str_token}"
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["detail"], "User is not found!")
        self.assertNotIn(doctor, list(clinic.doctors.all()))

        # Test No token available
        url = reverse("doctor_accept_invite", args=(clinic.id,))
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["detail"], "Token Arg Required.")
        self.assertNotIn(doctor, list(clinic.doctors.all()))

        # Test if no clinic invites
        doctor.clinic_invites.remove(clinic)
        doctor.save()

        str_token = token.encode(
            doctor.user.email, expiration_seconds=(60 * 60 * 24 * 7)
        )

        url = f"{reverse('doctor_accept_invite', args=(clinic.id,))}?token={str_token}"
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["detail"], "Invite not found!")
        self.assertNotIn(doctor, list(clinic.doctors.all()))

        # Test invalid token
        doctor.clinic_invites.add(clinic)
        doctor.save()

        str_token = token.encode(
            doctor.user.email, expiration_seconds=(60 * 60 * 24 * 7)
        )

        url = f"{reverse('doctor_accept_invite', args=(clinic.id,))}?token=invalidtoken"
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn(doctor, list(clinic.doctors.all()))

    def test_doctor_reject_clinic_invite(self):
        """
        Ensure invited doctor can reject clinic invite.
        """
        user = create_user()
        clinic = Clinic.objects.get_or_create(
            user=user, name="my clinic", phone="0718976234", email="myclinic@myapp.com"
        )[0]

        doctor = Doctor.objects.get_or_create(
            user=create_default_doctor(),
            speciality=Speciality.objects.get_or_create(name="dentist")[0],
        )[0]
        doctor.clinic_invites.add(clinic)
        doctor.save()

        str_token = token.encode(
            doctor.user.email, expiration_seconds=(60 * 60 * 24 * 7)
        )

        url = f"{reverse('doctor_reject_invite', args=(clinic.id,))}?token={str_token}"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["detail"], "Invite Rejected!")
        self.assertNotIn(doctor, list(clinic.doctors.all()))

        # Test new user invite
        user = MyUser.objects.create(phone="0716976234", email="newuser@myapp.com")
        doctor = Doctor.objects.get_or_create(
            user=user, speciality=Speciality.objects.get_or_create(name="dentist")[0]
        )[0]
        doctor.clinic_invites.add(clinic)
        doctor.save()

        str_token = token.encode(
            doctor.user.email, expiration_seconds=(60 * 60 * 24 * 7)
        )

        url = f"{reverse('doctor_reject_invite', args=(clinic.id,))}?token={str_token}"
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["detail"], "Invite Rejected!")
        self.assertNotIn(doctor, list(clinic.doctors.all()))
        self.assertFalse(Doctor.objects.filter(user=doctor.user).exists())
        self.assertFalse(MyUser.objects.filter(email=doctor.user.email).exists())

        # Test bad token invite
        doctor = Doctor.objects.get_or_create(
            user=create_default_doctor(),
            speciality=Speciality.objects.get_or_create(name="dentist")[0],
        )[0]
        doctor.clinic_invites.add(clinic)
        doctor.save()

        str_token = token.encode(
            doctor.user.phone, expiration_seconds=(60 * 60 * 24 * 7)
        )

        url = f"{reverse('doctor_reject_invite', args=(clinic.id,))}?token={str_token}"
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["detail"], "User is not found!")
        self.assertNotIn(doctor, list(clinic.doctors.all()))

        # Test No token available
        url = reverse("doctor_reject_invite", args=(clinic.id,))
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["detail"], "Token Arg Required.")
        self.assertNotIn(doctor, list(clinic.doctors.all()))

        # Test invalid token
        str_token = token.encode(
            doctor.user.email, expiration_seconds=(60 * 60 * 24 * 7)
        )

        url = f"{reverse('doctor_reject_invite', args=(clinic.id,))}?token=invalidtoken"
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn(doctor, list(clinic.doctors.all()))

        # Test if no clinic invites
        doctor = Doctor.objects.get_or_create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="dentist")[0],
        )[0]

        str_token = token.encode(
            doctor.user.email, expiration_seconds=(60 * 60 * 24 * 7)
        )

        url = f"{reverse('doctor_reject_invite', args=(clinic.id,))}?token={str_token}"
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["detail"], "Invite not found!")
        self.assertNotIn(doctor, list(clinic.doctors.all()))
