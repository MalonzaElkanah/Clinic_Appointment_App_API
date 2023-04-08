from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from clinic.models import (
    Patient,
    Prescription,
    Doctor,
    MedicalRecord,
    FavouriteDoctor,
    Appointment,
    Invoice,
    Bill,
    DoctorSchedule,
    TimeSlot,
)
from administrator.models import Speciality
from clinic.tests.utils import create_default_doctor, create_user

import datetime as dt


class ListCreateRetrieveUpdateDestroyPatientViewTests(APITestCase):
    def setUp(self):
        """
        Create user and Patient Object to be used
        through-out this Patient View Tests Case.
        """
        Patient.objects.get_or_create(user=create_user())
        Patient.objects.get_or_create(user=create_user())

    def test_list_patient(self):
        """
        Ensure Doctors can list all patients,
        patients user can only list their user profile,
        AnonymousUser will return empty user list
        """
        url = reverse("patient:patient_list_create")

        # check Doctor user can list all patients
        doctor = create_default_doctor()
        self.client.login(username=doctor.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), Patient.objects.count())
        self.client.logout()

        # check patiet can only list their patient profile
        patient = Patient.objects.create(user=create_user())
        self.client.login(username=patient.user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 1)
        self.assertEqual(
            response.json()["results"][0]["id"],
            patient.id,
        )
        self.assertEqual(
            response.json()["results"][0]["user"]["email"],
            patient.user.email,
        )
        self.client.logout()

        # check if AnonymousUser will return empty patient list
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 0)

    def test_create_patient(self):
        """
        Ensure you can register as patient.
        """
        url = reverse("patient:patient_list_create")
        data = {
            "user": {
                "email": "newpatient@myapp.com",
                "username": "newpatient",
                "password": "Pass1234",
                "first_name": "newpatient",
                "phone": "0712309876",
            }
        }
        patient_count = Patient.objects.count()
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Patient.objects.last().user.email, data["user"]["email"])
        self.assertEqual(Patient.objects.count(), patient_count + 1)

        # Create a patient that already exists
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Patient.objects.count(), patient_count + 1)

    def test_retrieve_patient(self):
        """
        Ensure a patient can retrieve their profile.
        Doctors can retrieve patient profile.
        """
        patient = Patient.objects.create(user=create_user())
        url = reverse("patient:patient_retrieve_update", args=(patient.id,))

        # Test if unautheticated user can retrieve
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("id", None), None)

        # check if Doctor can get a patient details
        doctor = create_default_doctor()
        self.client.login(username=doctor.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], patient.id)
        self.client.logout()

        # check if patient cannot retrieve another patient details
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get("id", None), None)
        self.client.logout()

        # check if patient can retrieve their own patient details
        self.client.login(username=patient.user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], patient.id)
        self.client.logout()

    def test_update_patient(self):
        """
        Ensure a patient can update their profile.
        """
        patient = Patient.objects.create(user=create_user())
        url = reverse("patient:patient_retrieve_update", args=(patient.id,))
        data = {
            "user": {
                "email": patient.user.email,
                "username": patient.user.username,
                "first_name": "oldpatient",
                "phone": "0712309876",
            }
        }

        # Test if unautheticated user cannot update
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(
            Patient.objects.get(id=patient.id).user.first_name,
            data["user"]["first_name"],
        )

        # Test if non owner cannot update
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Patient.objects.get(id=patient.id).user.first_name,
            data["user"]["first_name"],
        )
        self.client.logout()

        # Test if owner can update
        self.client.login(username=patient.user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Patient.objects.get(id=patient.id).user.first_name,
            data["user"]["first_name"],
        )
        self.client.logout()

    def test_destroy_patient(self):
        """
        Ensure a patient can delete their profile.
        """
        patient = Patient.objects.create(user=create_user())
        url = reverse("patient:patient_retrieve_update", args=(patient.id,))

        # Test if unautheticated user cannot delete
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Patient.objects.filter(id=patient.id).exists())

        # Test if non-owner cannot retrieve
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Patient.objects.filter(id=patient.id).exists())
        self.client.logout()

        # Test if admin user can retrieve
        self.client.login(username=patient.user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Patient.objects.filter(id=patient.id).exists())
        self.client.logout()


class PrescriptionViewTests(APITestCase):
    def setUp(self):
        """
        Create Prescription, Patient, Doctor Object to be used
        through-out this Prescription View Tests Case.
        """
        pass

    def test_list_prescription(self):
        """
        Ensure patients can list their prescription.
        Ensure doctors can list patients prescriptions.
        """
        patient = Patient.objects.get_or_create(user=create_user(name="patient1"))[0]
        patient2 = Patient.objects.get_or_create(user=create_user(name="patient2"))[0]
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        Prescription.objects.create(name="Asprin", patient=patient, doctor=doctor)
        Prescription.objects.create(name="Ibrofen", patient=patient, doctor=doctor)
        Prescription.objects.create(name="Asprin", patient=patient2, doctor=doctor)
        Prescription.objects.create(name="Ibrofen", patient=patient2, doctor=doctor)

        url = reverse("patient:prescription-list", args=(patient.id,))

        # check Doctor user can list patient's prescriptions
        doctor = create_default_doctor()
        self.client.login(username=doctor.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.json()["results"]),
            Prescription.objects.filter(patient=patient.id).count(),
        )
        self.client.logout()

        # check patient can only list their patient prescriptions
        self.client.login(username=patient.user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.json()["results"]),
            Prescription.objects.filter(patient=patient.id).count(),
        )
        for data in response.json()["results"]:
            self.assertEqual(data["patient"], patient.id)
        self.client.logout()

        # check if Patient cannot get other patients prescription list
        self.client.login(username=patient2.user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get("results", None), None)
        self.client.logout()

        # check if AnonymousUser will not return prescription list
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("results", None), None)

    def test_create_prescription(self):
        """
        Ensure only doctors can create patients prescriptions.
        """
        patient = Patient.objects.get_or_create(user=create_user(name="patient1"))[0]
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        url = reverse("patient:prescription-list", args=(patient.id,))
        prescription_count = Prescription.objects.filter(patient=patient.id).count()
        data = {
            "name": "Pencillin",
            "quantity": 40,
            "days": 13,
            "morning": True,
            "afternoon": True,
            "evening": False,
            "night": True,
            "patient": patient.id,
            "doctor": doctor.id,
        }

        # Test if unautheticated user can create
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            Prescription.objects.filter(patient=patient.id).count(), prescription_count
        )

        # Test if owner patient cannot create
        self.client.login(username=patient.user.username, password="Pass1234")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            Prescription.objects.filter(patient=patient.id).count(), prescription_count
        )
        self.client.logout()

        # Test if doctor user can create
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Prescription.objects.filter(patient=patient.id).count(),
            prescription_count + 1,
        )
        self.assertEqual(Prescription.objects.last().name, data["name"])
        self.client.logout()

    def test_retrieve_prescription(self):
        """
        Ensure patients can view details of their prescription.
        Ensure doctors can view details of the patients prescriptions.
        """
        patient = Patient.objects.get_or_create(user=create_user(name="patient1"))[0]
        patient2 = Patient.objects.get_or_create(user=create_user(name="patient2"))[0]
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        prescription = Prescription.objects.create(
            name="Asprin", patient=patient, doctor=doctor
        )

        url = reverse(
            "patient:prescription-detail",
            args=(
                patient.id,
                prescription.id,
            ),
        )

        # check Doctor user can get patient's prescription details
        doctor = create_default_doctor()
        self.client.login(username=doctor.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], prescription.id)
        self.client.logout()

        # check patient can only get details of their patient prescriptions
        self.client.login(
            username=prescription.patient.user.username, password="Pass1234"
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], prescription.id)
        self.client.logout()

        # check if Patient cannot get other patients prescription
        self.client.login(username=patient2.user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get("id", None), None)
        self.client.logout()

        # check if AnonymousUser will return no patient prescription
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("id", None), None)

    def test_update_prescription(self):
        """
        Ensure that only the doctor that created patients prescriptions
        can update.
        """
        patient = Patient.objects.get_or_create(user=create_user(name="patient1"))[0]
        patient2 = Patient.objects.get_or_create(user=create_user(name="patient2"))[0]
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        prescription = Prescription.objects.create(
            name="Asprin", patient=patient, doctor=doctor
        )
        data = {
            "name": "Pencillin",
            "quantity": 40,
            "days": 13,
            "morning": True,
            "afternoon": True,
            "evening": False,
            "night": True,
            "patient": patient.id,
            "doctor": doctor.id,
        }

        url = reverse(
            "patient:prescription-detail",
            args=(
                patient.id,
                prescription.id,
            ),
        )

        # Test if unautheticated user can update
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(
            Prescription.objects.get(id=prescription.id).name, data["name"]
        )

        # Test if patient owner cannot update prescription
        self.client.login(username=patient.user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Prescription.objects.get(id=prescription.id).name, data["name"]
        )
        self.client.logout()

        # Test if any patient cannot update other patient prescription
        self.client.login(username=patient2.user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Prescription.objects.get(id=prescription.id).name, data["name"]
        )
        self.client.logout()

        # Test if doctor can update
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Prescription.objects.get(id=prescription.id).name, data["name"]
        )
        self.client.logout()

    def test_destroy_prescription(self):
        """
        Ensure that only the doctor that created patients prescriptions
        can delete.
        """
        patient = Patient.objects.get_or_create(user=create_user(name="patient1"))[0]
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        prescription = Prescription.objects.create(
            name="Asprin", patient=patient, doctor=doctor
        )

        url = reverse(
            "patient:prescription-detail",
            args=(
                patient.id,
                prescription.id,
            ),
        )

        # Test if unautheticated user can delete
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Prescription.objects.filter(id=prescription.id).exists())

        # Test if patient owner cannot delete
        self.client.login(
            username=prescription.patient.user.username, password="Pass1234"
        )
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Prescription.objects.filter(id=prescription.id).exists())
        self.client.logout()

        # Test if admin user can retrieve
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Prescription.objects.filter(id=prescription.id).exists())
        self.client.logout()


class MedicalRecordViewTests(APITestCase):
    def setUp(self):
        """
        Create user, Patient, Doctor Object to be used
        through-out this MedicalRecord View Tests Case.
        """
        pass

    def test_list_medical_record(self):
        """
        Ensure patients can list their Medical Records.
        Ensure doctors can list patients Medical Records.
        """
        patient = Patient.objects.get_or_create(user=create_user(name="patient1"))[0]
        patient2 = Patient.objects.get_or_create(user=create_user(name="patient2"))[0]
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        MedicalRecord.objects.create(
            description="Asprin",
            patient=patient,
            doctor=doctor,
            date_recorded=dt.date.today(),
        )
        MedicalRecord.objects.create(
            description="Ibrofen",
            patient=patient,
            doctor=doctor,
            date_recorded=dt.date.today(),
        )
        MedicalRecord.objects.create(
            description="Asprin",
            patient=patient,
            doctor=doctor,
            date_recorded=dt.date.today(),
        )
        MedicalRecord.objects.create(
            description="Ibrofen",
            patient=patient,
            doctor=doctor,
            date_recorded=dt.date.today(),
        )

        url = reverse("patient:medicalrecord-list", args=(patient.id,))

        # check Doctor user can list patient's medical records
        doctor = create_default_doctor()
        self.client.login(username=doctor.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), MedicalRecord.objects.count())
        self.client.logout()

        # check patient can only list their patient medical records
        self.client.login(username=patient.user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.json()["results"]),
            MedicalRecord.objects.filter(patient=patient.id).count(),
        )
        for data in response.json()["results"]:
            self.assertEqual(data["patient"], patient.id)
        self.client.logout()

        # check if Patient cannot get other patients medical records list
        self.client.login(username=patient2.user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get("results", None), None)
        self.client.logout()

        # check if AnonymousUser will not return medical records list
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("results", None), None)

    def test_create_medical_record(self):
        """
        Ensure only doctors can create patients Medical Records.
        """
        patient = Patient.objects.get_or_create(user=create_user(name="patient1"))[0]
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        url = reverse("patient:medicalrecord-list", args=(patient.id,))
        record_count = MedicalRecord.objects.filter(patient=patient.id).count()
        data = {
            "description": "Pencillin",
            "date_recorded": dt.date.today(),
            "doctor": doctor.id,
            "patient": patient.id,
        }

        # Test if unautheticated user can create
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            MedicalRecord.objects.filter(patient=patient.id).count(), record_count
        )

        # Test if owner patient cannot create
        self.client.login(username=patient.user.username, password="Pass1234")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            MedicalRecord.objects.filter(patient=patient.id).count(), record_count
        )
        self.client.logout()

        # Test if doctor user can create
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            MedicalRecord.objects.filter(patient=patient.id).count(), record_count + 1
        )
        self.assertEqual(MedicalRecord.objects.last().description, data["description"])
        self.client.logout()

    def test_retrieve_medical_record(self):
        """
        Ensure patients can view details of their Medical Records.
        Ensure doctors can view details of the patients Medical Records.
        """
        patient = Patient.objects.get_or_create(user=create_user(name="patient1"))[0]
        patient2 = Patient.objects.get_or_create(user=create_user(name="patient2"))[0]
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        record = MedicalRecord.objects.create(
            description="Asprin",
            date_recorded=dt.date.today(),
            patient=patient,
            doctor=doctor,
        )

        url = reverse(
            "patient:medicalrecord-detail",
            args=(
                patient.id,
                record.id,
            ),
        )

        # check Doctor user can get patient's record details
        doctor = create_default_doctor()
        self.client.login(username=doctor.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], record.id)
        self.client.logout()

        # check patient can only get details of their patient record
        self.client.login(username=record.patient.user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], record.id)
        self.client.logout()

        # check if Patient cannot get other patients record
        self.client.login(username=patient2.user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get("id", None), None)
        self.client.logout()

        # check if AnonymousUser will return no patient record
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("id", None), None)

    def test_update_medical_record(self):
        """
        Ensure that only the doctor that created patient's Medical Record
        can update.
        """
        patient = Patient.objects.get_or_create(user=create_user(name="patient1"))[0]
        patient2 = Patient.objects.get_or_create(user=create_user(name="patient2"))[0]
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        record = MedicalRecord.objects.create(
            description="Asprin",
            date_recorded=dt.date.today(),
            patient=patient,
            doctor=doctor,
        )
        data = {
            "description": "Pencillin",
            "date_recorded": dt.date.today() - dt.timedelta(days=366),
            "doctor": doctor.id,
            "patient": patient.id,
        }

        url = reverse(
            "patient:medicalrecord-detail",
            args=(
                patient.id,
                record.id,
            ),
        )

        # Test if unautheticated user can update
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(
            MedicalRecord.objects.get(id=record.id).description, data["description"]
        )

        # Test if patient owner cannot update record
        self.client.login(username=patient.user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            MedicalRecord.objects.get(id=record.id).description, data["description"]
        )
        self.client.logout()

        # Test if any patient cannot update other patient record
        self.client.login(username=patient2.user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            MedicalRecord.objects.get(id=record.id).description, data["description"]
        )
        self.client.logout()

        # Test if doctor can update
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            MedicalRecord.objects.get(id=record.id).description, data["description"]
        )
        self.client.logout()

    def test_destroy_medical_record(self):
        """
        Ensure that only the doctor that created patient's Medical Record
        can delete.
        """
        patient = Patient.objects.get_or_create(user=create_user(name="patient1"))[0]
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        record = MedicalRecord.objects.create(
            description="Asprin",
            date_recorded=dt.date.today(),
            patient=patient,
            doctor=doctor,
        )

        url = reverse(
            "patient:medicalrecord-detail",
            args=(
                patient.id,
                record.id,
            ),
        )

        # Test if unautheticated user can delete
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(MedicalRecord.objects.filter(id=record.id).exists())

        # Test if patient owner cannot delete
        self.client.login(username=record.patient.user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(MedicalRecord.objects.filter(id=record.id).exists())
        self.client.logout()

        # Test if admin user can retrieve
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(MedicalRecord.objects.filter(id=record.id).exists())
        self.client.logout()


class FavouriteDoctorViewTests(APITestCase):
    def setUp(self):
        """
        Create user, Patient, Doctor Object to be used
        through-out this Favourite Doctor View Tests Case.
        """
        pass

    def test_list_favourite_doctors(self):
        """
        Ensure patients can list their Favourite Doctors.
        """
        patient = Patient.objects.get_or_create(user=create_user(name="patient1"))[0]
        patient2 = Patient.objects.get_or_create(user=create_user(name="patient2"))[0]
        doctor2 = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        FavouriteDoctor.objects.create(patient=patient, doctor=doctor)
        FavouriteDoctor.objects.create(patient=patient, doctor=doctor2)
        FavouriteDoctor.objects.create(patient=patient2, doctor=doctor)
        FavouriteDoctor.objects.create(patient=patient2, doctor=doctor2)

        url = reverse("patient:favourite-doctor_list_create")

        # check Doctor user cannot list patient's favourite doctor
        doctor = create_default_doctor()
        self.client.login(username=doctor.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get("results", None), None)
        self.client.logout()

        # check patient can only list their patient fav doc
        self.client.login(username=patient.user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.json()["results"]),
            FavouriteDoctor.objects.filter(patient=patient.id).count(),
        )
        for data in response.json()["results"]:
            self.assertEqual(data["patient"], patient.id)
        self.client.logout()

        # check if Patient2 can't get other patients fav list
        self.client.login(username=patient2.user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.json()["results"]),
            FavouriteDoctor.objects.filter(patient=patient2.id).count(),
        )
        for data in response.json()["results"]:
            self.assertEqual(data["patient"], patient2.id)
        self.client.logout()

        # check if AnonymousUser will not return fav doc
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("results", None), None)

    def test_create_favourite_doctor(self):
        """
        Ensure patients can Favourite Doctor.
        """
        patient = Patient.objects.get_or_create(user=create_user(name="patient1"))[0]
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        url = reverse("patient:favourite-doctor_list_create")
        count = FavouriteDoctor.objects.filter(patient=patient.id).count()
        data = {"doctor": doctor.id, "patient": patient.id}

        # Test if unautheticated user can create
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            FavouriteDoctor.objects.filter(patient=patient.id).count(), count
        )

        # Test if non-owner can create
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            FavouriteDoctor.objects.filter(patient=patient.id).count(), count
        )
        self.client.logout()

        # Test if patient user can create
        self.client.login(username=patient.user.username, password="Pass1234")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            FavouriteDoctor.objects.filter(patient=patient.id).count(), count + 1
        )
        self.assertEqual(FavouriteDoctor.objects.last().doctor.id, data["doctor"])
        self.client.logout()

    def test_destroy_favourite_doctor(self):
        """
        Ensure patients can remove doctor from their FavouriteDoctor.
        """
        patient = Patient.objects.get_or_create(user=create_user(name="patient1"))[0]
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        favourite = FavouriteDoctor.objects.create(patient=patient, doctor=doctor)

        url = reverse("patient:favourite-doctor_destroy", args=(favourite.id,))

        # Test if unautheticated user can delete
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(FavouriteDoctor.objects.filter(id=favourite.id).exists())

        # Test if non owner cannot delete
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(FavouriteDoctor.objects.filter(id=favourite.id).exists())
        self.client.logout()

        # Test if patient owner can retrieve
        self.client.login(username=favourite.patient.user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(FavouriteDoctor.objects.filter(id=favourite.id).exists())
        self.client.logout()


class AppointmentViewTests(APITestCase):
    def setUp(self):
        """
        Create user, Patient, Doctor Object to be used
        through-out this Appointment View Tests Case.
        """
        pass

    def test_list_appointment(self):
        """
        Ensure patients can list their Appointments.
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

        url = reverse("patient:appointment-list", args=(patient.id,))

        # check Doctor user cannot list patient's appointment-list
        doctor = create_default_doctor()
        self.client.login(username=doctor.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get("results", None), None)
        self.client.logout()

        # check patient can only list their patient appointment-list
        self.client.login(username=patient.user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.json()["results"]),
            Appointment.objects.filter(patient=patient.id).count(),
        )
        for data in response.json()["results"]:
            self.assertEqual(data["patient"], patient.id)
        self.client.logout()

        # check if Patient cannot get other patients appointment-list
        patient2 = Patient.objects.get_or_create(user=create_user(name="patient2"))[0]
        self.client.login(username=patient2.user.username, password="Pass1234")
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
        Ensure patients can create Appointments.
        """
        patient = Patient.objects.get_or_create(user=create_user(name="patient1"))[0]
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )
        url = reverse("patient:appointment-list", args=(patient.id,))
        count = Appointment.objects.filter(patient=patient.id).count()
        data = {
            "doctor": doctor.id,
            "date_of_appointment": timezone.make_aware(
                dt.datetime.utcnow() + dt.timedelta(days=7)
            ),
            "purpose": "tooth replacement",
            "status": "CONFIRMED",
            "patient": patient.id,
        }

        # Test if unautheticated user can create
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Appointment.objects.filter(patient=patient.id).count(), count)

        # Test if non-owner can create
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Appointment.objects.filter(patient=patient.id).count(), count)
        self.client.logout()

        # Test if owner cannot create appointment if doc has no schdl
        self.client.login(username=patient.user.username, password="Pass1234")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()["detail"], "Doctor has not created a schedule."
        )
        self.assertEqual(Appointment.objects.filter(patient=patient.id).count(), count)

        # Add schedule to doctor
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

        # Test if owner cannot create appointment if unavailable appointment date
        d_o_a = dt.datetime(
            (dt.date.today() + dt.timedelta(days=7)).year,
            (dt.date.today() + dt.timedelta(days=7)).month,
            (dt.date.today() + dt.timedelta(days=7)).day,
            timeslot.end_time.hour + 1,
            timeslot.end_time.minute,
        )
        data.update({"date_of_appointment": timezone.make_aware(d_o_a)})
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()["detail"],
            "Invalid Date: Check the Doctor Appointment Schedule before booking.",
        )
        self.assertEqual(Appointment.objects.filter(patient=patient.id).count(), count)

        # Test if owner can create appointment in an available appointment date
        d_o_a = dt.datetime(
            (dt.date.today() + dt.timedelta(days=7)).year,
            (dt.date.today() + dt.timedelta(days=7)).month,
            (dt.date.today() + dt.timedelta(days=7)).day,
            timeslot.start_time.hour,
            timeslot.start_time.minute,
        )
        data.update({"date_of_appointment": timezone.make_aware(d_o_a)})
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Appointment.objects.filter(patient=patient.id).count(), count + 1
        )
        self.assertEqual(Appointment.objects.last().doctor.id, data["doctor"])
        self.client.logout()

        # Test if owner cannot create appointment in a Fully Booked Appointment.
        patient2 = Patient.objects.get_or_create(user=create_user(name="patient2"))[0]
        url = reverse("patient:appointment-list", args=(patient2.id,))
        data.update({"patient": patient2.id})
        count2 = Appointment.objects.filter(patient=patient2.id).count()
        self.client.login(username=patient2.user.username, password="Pass1234")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["detail"], "Timeslot is Fully Booked.")
        self.assertEqual(
            Appointment.objects.filter(patient=patient2.id).count(), count2
        )
        self.client.logout()

    def test_retrieve_appointment(self):
        """
        Ensure patients can view details of their Appointments.
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

        url = reverse("patient:appointment-detail", args=(patient.id, appointment.id))

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

        # Test if non owner patient cannot retrieve models
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get("id", None), None)
        self.client.logout()

        # Test if autheticated owner doctor cannot retrieve models
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get("id", None), None)
        self.client.logout()

        # Test if patient can retrieve models
        self.client.login(username=patient.user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], appointment.id)
        self.client.logout()

    def test_update_appointment(self):
        """
        Ensure patients cannot update their Appointments.
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

        url = reverse("patient:appointment-detail", args=(patient.id, appointment.id))

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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Appointment.objects.get(id=appointment.id).status, data["status"]
        )
        self.client.logout()

        # Test if owner patient cannot update models
        self.client.login(
            username=appointment.patient.user.username, password="Pass1234"
        )
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertNotEqual(
            Appointment.objects.get(id=appointment.id).status, data["status"]
        )
        self.client.logout()

    def test_destroy_appointment(self):
        """
        Ensure patients cannot delete their Appointments.
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

        url = reverse("patient:appointment-detail", args=(patient.id, appointment.id))

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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Appointment.objects.filter(id=appointment.id).exists())
        self.client.logout()

        # Test if owner patient cannot delete models
        self.client.login(
            username=appointment.patient.user.username, password="Pass1234"
        )
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertTrue(Appointment.objects.filter(id=appointment.id).exists())
        self.client.logout()

    def test_reschedule_appointment(self):
        """
        Ensure patient can update reschedule appointment.
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
                dt.datetime.utcnow() + dt.timedelta(days=7)
            ),
            purpose="tooth replacement",
            status="WAITING",
        )

        url = reverse(
            "patient:appointment-reschedule", args=(patient.id, appointment.id)
        )

        data = {
            "date_of_appointment": timezone.now() + dt.timedelta(days=5),
        }

        # Test if unautheticated user can reschedule appointment
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(
            Appointment.objects.get(id=appointment.id).status, "RESCHEDULED"
        )

        # Test if non owner patient cannot reschedule appointment
        user = create_user()
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Appointment.objects.get(id=appointment.id).status, "RESCHEDULED"
        )
        self.client.logout()

        # Test if non-owner doctor cannot reschedule appointment
        user = create_user(name="d.user2", role="DOCTOR")
        self.client.login(username=user.username, password="Pass1234")
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Appointment.objects.get(id=appointment.id).status, "RESCHEDULED"
        )
        self.client.logout()

        # Test if owner doctor cannot reschedule appointment
        self.client.login(
            username=appointment.doctor.user.username, password="Pass1234"
        )
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Appointment.objects.get(id=appointment.id).status, "RESCHEDULED"
        )
        self.client.logout()

        # Test if owner patient can reschedule appointment
        self.client.login(
            username=appointment.patient.user.username, password="Pass1234"
        )
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()["detail"],
            "Doctor has not created a schedule.",
        )
        self.assertNotEqual(
            Appointment.objects.get(id=appointment.id).status, "RESCHEDULED"
        )

        # Add schedule to doctor
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

        # Test if owner cannot create appointment if unavailable appointment date
        d_o_a = dt.datetime(
            (dt.date.today() + dt.timedelta(days=7)).year,
            (dt.date.today() + dt.timedelta(days=7)).month,
            (dt.date.today() + dt.timedelta(days=7)).day,
            timeslot.end_time.hour + 1,
            timeslot.end_time.minute,
        )
        data.update({"date_of_appointment": timezone.make_aware(d_o_a)})
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()["detail"],
            "Invalid Date: Check the Doctor Appointment Schedule before booking.",
        )
        self.assertNotEqual(
            Appointment.objects.get(id=appointment.id).status, "RESCHEDULED"
        )

        # Test if owner can create appointment in an available appointment date
        d_o_a = dt.datetime(
            (dt.date.today() + dt.timedelta(days=7)).year,
            (dt.date.today() + dt.timedelta(days=7)).month,
            (dt.date.today() + dt.timedelta(days=7)).day,
            timeslot.start_time.hour,
            timeslot.start_time.minute,
        )
        data.update({"date_of_appointment": timezone.make_aware(d_o_a)})
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Appointment.objects.get(id=appointment.id).status, "RESCHEDULED"
        )
        self.client.logout()

    def test_cancel_appointment(self):
        """
        Ensure a patient can cancel appointment.
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

        url = reverse("patient:appointment-cancel", args=(patient.id, appointment.id))

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

        # Test if owner doctor can cancel appointment
        self.client.login(
            username=appointment.doctor.user.username, password="Pass1234"
        )
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Appointment.objects.get(id=appointment.id).status, "CANCELED"
        )
        self.client.logout()

        # Test if owner patient can cancel appointment
        self.client.login(
            username=appointment.patient.user.username, password="Pass1234"
        )
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Appointment.objects.get(id=appointment.id).status, "CANCELED")
        self.client.logout()


class InvoiceViewTests(APITestCase):
    def setUp(self):
        """
        Create user, Patient, Doctor Object to be used
        through-out this Invoice View Tests Case.
        """
        pass

    def test_list_invoice(self):
        """
        Ensure patients can list their Invoice.
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
        appointment2 = Appointment.objects.create(
            patient=patient,
            doctor=doctor2,
            date_of_appointment=timezone.make_aware(
                dt.datetime.utcnow() + dt.timedelta(days=5)
            ),
            purpose="tooth replacement",
            status="CONFIRMED",
        )

        invoice = Invoice.objects.create(appointment=appointment)
        for x in range(1, 10):
            bill = Bill.objects.create(
                name=f"Bill-{x}",
                appointment=appointment,
                amount=(100.0 * x),
                paid=False,
            )
            bill.invoice_set.add(invoice)
            bill.save()

        invoice = Invoice.objects.create(appointment=appointment2)
        for x in range(1, 10):
            bill = Bill.objects.create(
                name=f"Bill-k{x}",
                appointment=appointment2,
                amount=(50.0 * x),
                paid=True,
            )
            bill.invoice_set.add(invoice)
            bill.save()

        url = reverse("patient:invoice-list", args=(patient.id,))

        # check Doctor user cannot list patient's appointment-list
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get("results", None), None)
        self.client.logout()

        # check patient can only list their patient appointment-list
        self.client.login(username=patient.user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.json()["results"]),
            Invoice.objects.filter(appointment__patient=patient.id).count(),
        )
        for data in response.json()["results"]:
            appointment_id = data["appointment"]
            self.assertEqual(
                Appointment.objects.get(id=appointment_id).patient.id, patient.id
            )
        self.client.logout()

        # check if Patient cannot get other patients appointment-list
        patient2 = Patient.objects.get_or_create(user=create_user(name="patient2"))[0]
        self.client.login(username=patient2.user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get("results", None), None)
        self.client.logout()

        # check if AnonymousUser will not return appointment-list
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("results", None), None)

    def test_retrieve_invoice(self):
        """
        Ensure patients can view details of their Invoice.
        """
        patient = Patient.objects.get_or_create(user=create_user(name="patient1"))[0]
        patient2 = Patient.objects.get_or_create(user=create_user(name="patient2"))[0]
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

        invoice = Invoice.objects.create(appointment=appointment)

        for x in range(1, 10):
            bill = Bill.objects.create(
                name=f"Bill-{x}",
                appointment=appointment,
                amount=(100.0 * x),
                paid=False,
            )
            bill.invoice_set.add(invoice)
            bill.save()

        url = reverse(
            "patient:invoice-detail",
            args=(
                patient.id,
                invoice.id,
            ),
        )

        # check Doctor user cannot get patient's invoices
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get("id", None), None)
        self.client.logout()

        # check patient can get details of their invoces
        self.client.login(
            username=invoice.appointment.patient.user.username, password="Pass1234"
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], invoice.id)
        self.client.logout()

        # check if Patient cannot get other patients record
        self.client.login(username=patient2.user.username, password="Pass1234")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get("id", None), None)
        self.client.logout()

        # check if AnonymousUser will return no patient record
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("id", None), None)

    def test_not_create_invoice(self):
        """
        Ensure patients cannot create their Invoice.
        """
        patient = Patient.objects.get_or_create(user=create_user(name="patient1"))[0]
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )

        url = reverse("patient:invoice-list", args=(patient.id,))
        count = Invoice.objects.filter(appointment__patient=patient.id).count()
        data = {"patient": patient.id}

        # Test if unautheticated user cannot create
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            Invoice.objects.filter(appointment__patient=patient.id).count(), count
        )

        # Test if non-owner cannot create
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            Invoice.objects.filter(appointment__patient=patient.id).count(), count
        )
        self.client.logout()

        # Test if patient user cannot create
        self.client.login(username=patient.user.username, password="Pass1234")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            Invoice.objects.filter(appointment__patient=patient.id).count(), count
        )
        self.client.logout()

    def test_not_update_invoice(self):
        """
        Ensure patients cannot update their Invoice.
        """
        patient = Patient.objects.get_or_create(user=create_user(name="patient1"))[0]
        patient2 = Patient.objects.get_or_create(user=create_user(name="patient2"))[0]
        doctor = Doctor.objects.create(
            user=create_user(role="DOCTOR"),
            speciality=Speciality.objects.get_or_create(name="Test")[0],
        )

        data = {"doctor": doctor.id, "patient": patient.id}

        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date_of_appointment=timezone.make_aware(
                dt.datetime.utcnow() + dt.timedelta(days=7)
            ),
            purpose="tooth replacement",
            status="CONFIRMED",
        )

        invoice = Invoice.objects.create(appointment=appointment)

        for x in range(1, 10):
            bill = Bill.objects.create(
                name=f"Bill-{x}",
                appointment=appointment,
                amount=(100.0 * x),
                paid=False,
            )
            bill.invoice_set.add(invoice)
            bill.save()

        url = reverse(
            "patient:invoice-detail",
            args=(
                patient.id,
                invoice.id,
            ),
        )

        # Test if unautheticated user cannot update
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test if patient owner cannot update record
        self.client.login(username=patient.user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.client.logout()

        # Test if any patient cannot update other patient invoice
        self.client.login(username=patient2.user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()

        # Test if doctor cannot update
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()

    def test_not_destroy_invoice(self):
        """
        Ensure patients cannot remove their Invoice.
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
                dt.datetime.utcnow() + dt.timedelta(days=7)
            ),
            purpose="tooth replacement",
            status="CONFIRMED",
        )

        invoice = Invoice.objects.create(appointment=appointment)

        for x in range(1, 10):
            bill = Bill.objects.create(
                name=f"Bill-{x}",
                appointment=appointment,
                amount=(100.0 * x),
                paid=False,
            )
            bill.invoice_set.add(invoice)
            bill.save()

        url = reverse(
            "patient:invoice-detail",
            args=(
                patient.id,
                invoice.id,
            ),
        )

        # Test if unautheticated user can delete
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Invoice.objects.filter(id=invoice.id).exists())

        # Test if non owner cannot delete
        self.client.login(username=doctor.user.username, password="Pass1234")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Invoice.objects.filter(id=invoice.id).exists())
        self.client.logout()

        # Test if patient owner can retrieve
        self.client.login(
            username=invoice.appointment.patient.user.username, password="Pass1234"
        )
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertTrue(Invoice.objects.filter(id=invoice.id).exists())
        self.client.logout()
