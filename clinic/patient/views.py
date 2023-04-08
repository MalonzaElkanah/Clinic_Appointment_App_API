from rest_framework import generics
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from clinic.patient.permissions import (
    IsOwnerDoctorOrReadOnly,
    IsDoctorOrReadOnly,
    IsOwnerOrDoctor,
    # IsOwnerDoctorOrIsOwnerPatient,
    IsOwnerPatient,
    IsOwnerOrDoctorReadOnly,
    IsOwnerPatientInvoice,
)
from clinic.models import (
    Patient,
    Prescription,
    MedicalRecord,
    FavouriteDoctor,
    Appointment,
    Invoice,
)
from clinic.viewsets import CreateListRetrieveViewSet
from clinic.patient.serializers import (
    PatientSerializer,
    PrescriptionSerializer,
    MedicalRecordSerializer,
    FavouriteDoctorSerializer,
    AppointmentSerializer,
    InvoiceSerializer,
    AppointmentRescheduleSerializer,
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
            raise MyCustomException("Error: Patient not Found", code=403)
        return Prescription.objects.filter(patient=patients[0].id)

    def perform_create(self, serializer):
        patients = Patient.objects.filter(id=self.kwargs["patient_pk"])
        if patients.count() < 1:
            raise MyCustomException("Error: You are not a Patient", code=403)
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
            raise MyCustomException("Error: Patient not Found", code=403)
        return MedicalRecord.objects.filter(patient=patients[0].id)

    def perform_create(self, serializer):
        patients = Patient.objects.filter(id=self.kwargs["patient_pk"])
        if patients.count() < 1:
            raise MyCustomException("Error: You are not a Patient", code=403)
        serializer.save(patient=patients[0])


class ListCreateFavouriteDoctor(generics.ListCreateAPIView):
    queryset = FavouriteDoctor.objects.all()
    serializer_class = FavouriteDoctorSerializer
    permission_classes = [IsAuthenticated, IsOwnerPatient]

    def get_queryset(self):
        patients = Patient.objects.filter(user=self.request.user.id)
        if patients.count() < 1:
            raise MyCustomException("Error: You are not a Patient", code=403)
        return FavouriteDoctor.objects.filter(patient=patients[0].id)

    def perform_create(self, serializer):
        patients = Patient.objects.filter(user=self.request.user.id)
        if patients.count() < 1:
            raise MyCustomException("Error: You are not a Patient", code=403)
        serializer.save(patient=patients[0])


class DestroyFavouriteDoctor(generics.DestroyAPIView):
    queryset = FavouriteDoctor.objects.all()
    serializer_class = FavouriteDoctorSerializer
    permission_classes = [IsAuthenticated, IsOwnerPatient]


class AppointmentViewSet(CreateListRetrieveViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated, IsOwnerPatient]

    def get_queryset(self):
        patients = Patient.objects.filter(id=self.kwargs["patient_pk"])
        if patients.count() < 1:
            raise MyCustomException("Error: Patient not Found")
        return Appointment.objects.filter(patient=patients[0].id)

    def get_object(self):
        patients = Patient.objects.filter(id=self.kwargs["patient_pk"])
        if not patients.exists():
            raise MyCustomException("Error: Patient not Found", code=404)

        appointment = Appointment.objects.filter(
            id=self.kwargs["pk"], patient=patients.first().id
        )
        if not appointment.exists():
            raise MyCustomException("Error: Appointment not Found", code=404)

        return appointment.first()

    def perform_create(self, serializer):
        patients = Patient.objects.filter(id=self.kwargs["patient_pk"])
        if patients.count() < 1:
            raise MyCustomException("Error: You are not a Patient", code=403)
        date_time = serializer.validated_data.get("date_of_appointment", None)
        doctor = serializer.validated_data.get("doctor", 0)
        if date_time is not None:
            valid_date = validate_appointment_date(int(doctor.id), date_time)
            if valid_date["validated"] is False:
                raise MyCustomException(valid_date["message"])
        serializer.save(patient=patients[0], status="WAITING", amount=doctor.pricing)

    @action(detail=True, methods=["patch"])
    def reschedule(self, request, pk=None, **kwargs):
        instance = self.get_object()

        if request.user.id == instance.patient.user.id:
            if instance.status.upper() in ["CANCELED", "COMPLETED"]:
                raise MyCustomException(
                    f"Error: This appointments has been {instance.status}."
                )

            serializer = AppointmentRescheduleSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            date_time = serializer.validated_data.get("date_of_appointment", None)
            if date_time is None or date_time == instance.date_of_appointment:
                raise MyCustomException(
                    "Error: Enter new 'date_of_appointment' when rescheduling appointments."
                )

            # Check change in date of appontment is valid
            valid_date = validate_appointment_date(instance.doctor.id, date_time)
            if valid_date["validated"] is False:
                raise MyCustomException(valid_date["message"])

            instance.date_of_appointment = date_time
            instance.status = "RESCHEDULED"
            instance.save()
            # TODO
            # Notify doc change in date of appointment

            return Response({"detail": "Date of Appointment Updated"})
        else:
            raise MyCustomException("Appointment Patient Only", code=403)

    @action(detail=True, methods=["delete"])
    def cancel(self, request, pk=None, **kwargs):
        instance = self.get_object()

        if request.user.id == instance.patient.user.id:
            if instance.status.upper() in ["CANCELED", "COMPLETED", "PAID"]:
                raise MyCustomException(
                    f"Error: This appointments has already been {instance.status}."
                )

            instance.status = "CANCELED"
            instance.save()
            # TODO
            # Notify doc change in appointment status

            return Response({"detail": "Appointment has been Canceled"})
        else:
            raise MyCustomException("Appointment Patient Only", code=403)


class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated, IsOwnerPatientInvoice]

    def get_queryset(self):
        patients = Patient.objects.filter(id=self.kwargs["patient_pk"])
        if patients.count() < 1:
            raise MyCustomException("Error: Patient not Found")
        return Invoice.objects.filter(appointment__patient=patients[0].id)
