from rest_framework import generics
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from clinic.patient.permissions import (
    IsOwnerDoctorOrReadOnly,
    IsDoctorOrReadOnly,
    IsOwnerOrDoctor,
    IsOwnerDoctorOrIsOwnerPatient,
    IsOwnerPatient,
    IsOwnerOrDoctorReadOnly,
)
from clinic.models import (
    Patient,
    Prescription,
    MedicalRecord,
    FavouriteDoctor,
    Appointment,
    Invoice,
)
from clinic.patient.serializers import (
    PatientSerializer,
    PrescriptionSerializer,
    MedicalRecordSerializer,
    FavouriteDoctorSerializer,
    AppointmentSerializer,
    InvoiceSerializer,
)
from clinic.utils import validate_appointment_date

from mylib.common import MyCustomException


class ListCreatePatient(generics.ListCreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

    def get_queryset(self):
        """
        Show Patient Data to Doctors Only or OWNER
        """
        if self.request.user.is_authenticated:
            if self.request.user.role.name == "PATIENT":
                return Patient.objects.filter(user=self.request.user.id)
            elif self.request.user.role.name == "DOCTOR":
                return Patient.objects.all()
        return Patient.objects.filter(id=0)


class RetrieveUpdateDestroyPatient(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrDoctorReadOnly]


class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [
        IsAuthenticated,
        IsOwnerDoctorOrReadOnly,
        IsDoctorOrReadOnly,
        IsOwnerOrDoctor,
    ]

    def get_queryset(self):
        patients = Patient.objects.filter(id=self.kwargs["patient_pk"])
        if patients.count() < 1:
            raise MyCustomException("Error: Patient not Found")
        return Prescription.objects.filter(patient=patients[0].id)

    def perform_create(self, serializer):
        patients = Patient.objects.filter(id=self.kwargs["patient_pk"])
        if patients.count() < 1:
            raise MyCustomException("Error: You are not a Patient")
        serializer.save(patient=patients[0])


class MedicalRecordViewSet(viewsets.ModelViewSet):
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer
    permission_classes = [
        IsAuthenticated,
        IsOwnerDoctorOrReadOnly,
        IsDoctorOrReadOnly,
        IsOwnerOrDoctor,
    ]

    def get_queryset(self):
        patients = Patient.objects.filter(id=self.kwargs["patient_pk"])
        if patients.count() < 1:
            raise MyCustomException("Error: Patient not Found")
        return MedicalRecord.objects.filter(patient=patients[0].id)

    def perform_create(self, serializer):
        patients = Patient.objects.filter(id=self.kwargs["patient_pk"])
        if patients.count() < 1:
            raise MyCustomException("Error: You are not a Patient")
        serializer.save(patient=patients[0])


class FavouriteDoctorViewSet(viewsets.ModelViewSet):
    queryset = FavouriteDoctor.objects.all()
    serializer_class = FavouriteDoctorSerializer
    permission_classes = [IsAuthenticated, IsOwnerPatient]

    def get_queryset(self):
        patients = Patient.objects.filter(id=self.kwargs["patient_pk"])
        if patients.count() < 1:
            raise MyCustomException("Error: Patient not Found")
        return FavouriteDoctor.objects.filter(patient=patients[0].id)

    def perform_create(self, serializer):
        patients = Patient.objects.filter(id=self.kwargs["patient_pk"])
        if patients.count() < 1:
            raise MyCustomException("Error: You are not a Patient")
        serializer.save(patient=patients[0])


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated, IsOwnerPatient]

    def get_queryset(self):
        patients = Patient.objects.filter(id=self.kwargs["patient_pk"])
        if patients.count() < 1:
            raise MyCustomException("Error: Patient not Found")
        return Appointment.objects.filter(patient=patients[0].id)

    def perform_create(self, serializer):
        patients = Patient.objects.filter(id=self.kwargs["patient_pk"])
        if patients.count() < 1:
            raise MyCustomException("Error: You are not a Patient")
        date_time = serializer.validated_data.get("date_of_appointment", None)
        doctor = serializer.validated_data.get("doctor", 0)
        if date_time is not None:
            valid_date = validate_appointment_date(int(doctor.id), date_time)
            if valid_date["validated"] is False:
                raise MyCustomException(valid_date["message"])
        serializer.save(patient=patients[0], status="WAITING", amount=doctor.pricing)


class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated, IsOwnerDoctorOrIsOwnerPatient]

    def get_queryset(self):
        patients = Patient.objects.filter(id=self.kwargs["patient_pk"])
        if patients.count() < 1:
            raise MyCustomException("Error: Patient not Found")
        return Invoice.objects.filter(appointment__patient=patients[0].id)
