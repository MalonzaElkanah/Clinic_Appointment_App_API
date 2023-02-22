from rest_framework import generics
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from client.permissions import IsOwnerOrReadOnly
from clinic.doctor.permissions import (
    IsOwnerDoctorOrReadOnly, IsOwnerDoctorOrPatientPOSTOnly, IsOwnerReviewOrDoctorReadOnly
)
from clinic.models import (
    Doctor, Education, Experience, Award, Membership, Registration,
    DoctorSchedule, TimeSlot, SocialMedia, Appointment, AppoinmentReview, Patient
)
from clinic.doctor.serializers import (
    DoctorSerializer, EducationSerializer, ExperienceSerializer,
    AwardSerializer, MembershipSerializer, RegistrationSerializer,
    DoctorScheduleSerializer, TimeSlotSerializer, SocialMediaSerializer,
    ReviewSerializer, AppointmentSerializer
)

from mylib.common import MyCustomException

import datetime as dt
# Create your views here.


class ListCreateDoctor(generics.ListCreateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = []


class RetrieveUpdateDestroyDoctor(generics.RetrieveUpdateDestroyAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


class EducationViewSet(viewsets.ModelViewSet):
    queryset = Education.objects.all()
    serializer_class = EducationSerializer
    permission_classes = [IsAuthenticated, IsOwnerDoctorOrReadOnly]

    def get_queryset(self):
        doctors = Doctor.objects.filter(id=self.kwargs['doctor_pk'])
        if doctors.count() < 1:
            raise MyCustomException("Error: Doctor not Found")
        return Education.objects.filter(doctor=doctors[0].id)

    def perform_create(self, serializer):
        doctor = Doctor.objects.filter(user=self.request.user.id)
        if doctor.count() < 1:
            raise MyCustomException("Error: You are not a Doctor")
        serializer.save(doctor=doctor[0])


class ExperienceViewSet(viewsets.ModelViewSet):
    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer
    permission_classes = [IsAuthenticated, IsOwnerDoctorOrReadOnly]

    def get_queryset(self):
        doctors = Doctor.objects.filter(id=self.kwargs['doctor_pk'])
        if doctors.count() < 1:
            raise MyCustomException("Error: Doctor not Found")
        return Experience.objects.filter(doctor=doctors[0].id)

    def perform_create(self, serializer):
        doctor = Doctor.objects.filter(user=self.request.user.id)
        if doctor.count() < 1:
            raise MyCustomException("Error: You are not a Doctor")
        serializer.save(doctor=doctor[0])


class AwardViewSet(viewsets.ModelViewSet):
    queryset = Award.objects.all()
    serializer_class = AwardSerializer
    permission_classes = [IsAuthenticated, IsOwnerDoctorOrReadOnly]

    def get_queryset(self):
        doctors = Doctor.objects.filter(id=self.kwargs['doctor_pk'])
        if doctors.count() < 1:
            raise MyCustomException("Error: Doctor not Found")
        return Award.objects.filter(doctor=doctors[0].id)

    def perform_create(self, serializer):
        doctor = Doctor.objects.filter(user=self.request.user.id)
        if doctor.count() < 1:
            raise MyCustomException("Error: You are not a Doctor")
        serializer.save(doctor=doctor[0])


class MembershipViewSet(viewsets.ModelViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated, IsOwnerDoctorOrReadOnly]

    def get_queryset(self):
        doctors = Doctor.objects.filter(id=self.kwargs['doctor_pk'])
        if doctors.count() < 1:
            raise MyCustomException("Error: Doctor not Found")
        return Membership.objects.filter(doctor=doctors[0].id)

    def perform_create(self, serializer):
        doctor = Doctor.objects.filter(user=self.request.user.id)
        if doctor.count() < 1:
            raise MyCustomException("Error: You are not a Doctor")
        serializer.save(doctor=doctor[0])


class RegistrationViewSet(viewsets.ModelViewSet):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = [IsAuthenticated, IsOwnerDoctorOrReadOnly]

    def get_queryset(self):
        doctors = Doctor.objects.filter(id=self.kwargs['doctor_pk'])
        if doctors.count() < 1:
            raise MyCustomException("Error: Doctor not Found")
        return Registration.objects.filter(doctor=doctors[0].id)

    def perform_create(self, serializer):
        doctor = Doctor.objects.filter(user=self.request.user.id)
        if doctor.count() < 1:
            raise MyCustomException("Error: You are not a Doctor")
        serializer.save(doctor=doctor[0])


class DoctorScheduleViewSet(viewsets.ModelViewSet):
    queryset = DoctorSchedule.objects.all()
    serializer_class = DoctorScheduleSerializer
    permission_classes = [IsAuthenticated, IsOwnerDoctorOrReadOnly]

    def get_queryset(self):
        doctors = Doctor.objects.filter(id=self.kwargs['doctor_pk'])
        if doctors.count() < 1:
            raise MyCustomException("Error: Doctor not Found")
        return DoctorSchedule.objects.filter(doctor=doctors[0].id)

    def perform_create(self, serializer):
        doctor = Doctor.objects.filter(user=self.request.user.id)
        if doctor.count() < 1:
            raise MyCustomException("Error: You are not a Doctor")

        # Validate only the timeslot belongs to the doctor
        time_slots = serializer.validated_data.get("time_slot")
        print(time_slots)
        my_time_slots = TimeSlot.objects.filter(doctor=doctor[0].id)
        for slot in time_slots:
            if slot not in my_time_slots:
                raise MyCustomException(
                    f"Error: {slot} time slot is unauthorized. Choose a valid one."
                )

        # Validate only one Instance of Day
        day = serializer.validated_data.get("day")
        schedules = self.get_queryset()
        for schedule in schedules:
            if schedule.day == day:
                raise MyCustomException(
                    "Error: {} schedule has already been created.".format(day)
                )

        serializer.save(doctor=doctor[0])


class TimeSlotViewSet(viewsets.ModelViewSet):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    permission_classes = [IsAuthenticated, IsOwnerDoctorOrReadOnly]

    def get_queryset(self):
        doctors = Doctor.objects.filter(id=self.kwargs['doctor_pk'])
        if doctors.count() < 1:
            raise MyCustomException("Error: Doctor not Found")
        return TimeSlot.objects.filter(doctor=doctors[0].id)

    def perform_create(self, serializer):
        doctor = Doctor.objects.filter(user=self.request.user.id)
        if doctor.count() < 1:
            raise MyCustomException("Error: You are not a Doctor")
        serializer.save(doctor=doctor[0])


class SocialMediaViewSet(viewsets.ModelViewSet):
    queryset = SocialMedia.objects.all()
    serializer_class = SocialMediaSerializer
    permission_classes = [IsAuthenticated, IsOwnerDoctorOrReadOnly]

    def get_queryset(self):
        doctors = Doctor.objects.filter(id=self.kwargs['doctor_pk'])
        if doctors.count() < 1:
            raise MyCustomException("Error: Doctor not Found")
        return SocialMedia.objects.filter(doctor=doctors[0].id)

    def perform_create(self, serializer):
        doctor = Doctor.objects.filter(user=self.request.user.id)
        if doctor.count() < 1:
            raise MyCustomException("Error: You are not a Doctor")
        serializer.save(doctor=doctor[0])


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated, IsOwnerDoctorOrPatientPOSTOnly]

    def get_queryset(self):
        doctors = Doctor.objects.filter(id=self.kwargs['doctor_pk'])
        if doctors.count() < 1:
            raise MyCustomException("Error: Doctor not Found")
        return Appointment.objects.filter(doctor=doctors[0].id)

    def perform_create(self, serializer):
        # Check request.user.role is patient or owner doctor
        user = self.request.user
        if user.role.name == "DOCTOR":
            doctor = Doctor.objects.filter(user=user.id)
            if doctor.count() < 1:
                raise MyCustomException("Error: Doctor does not Exist.")
            date_time = serializer.validated_data.get('date_of_appointment', None)
            if date_time is not None:
                valid_date = validate_appointment_date(doctor[0].id, date_time)
                if valid_date["validated"] is False:
                    raise MyCustomException(valid_date["message"])
            serializer.save(doctor=doctor[0], status='WAITING', amount=doctor[0].pricing)
        elif user.role.name == "PATIENT":
            patients = Patient.objects.filter(user=user.id)
            if patients.count() < 1:
                raise MyCustomException("Error: Patient does not Exist.")

            doctors = Doctor.objects.filter(id=self.kwargs['doctor_pk'])
            if doctors.count() < 1:
                raise MyCustomException("Error: Doctor not Found")
            date_time = serializer.validated_data.get('date_of_appointment', None)
            if date_time is not None:
                valid_date = validate_appointment_date(doctors[0].id, date_time)
                if valid_date["validated"] is False:
                    raise MyCustomException(valid_date["message"])
            serializer.save(
                patient=patients[0],
                doctor=doctors[0],
                status='WAITING',
                amount=doctors[0].pricing
            )
        else:
            raise MyCustomException("Error: You don't have permissions to create Appointments.")


class ReviewViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AppoinmentReview.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsOwnerReviewOrDoctorReadOnly]

    def get_queryset(self):
        doctors = Doctor.objects.filter(id=self.kwargs['doctor_pk'])
        if doctors.count() < 1:
            raise MyCustomException("Error: Doctor not Found")
        return AppoinmentReview.objects.filter(appointment__doctor=doctors[0].id)


def validate_appointment_date(doctor, date_time):
    schedules = DoctorSchedule.objects.filter(doctor=doctor)
    if schedules.count() > 0:
        # today = dt.date.today()
        # tomorrow = today + dt.timedelta(days=1)
        for schdl in schedules:
            if str(schdl.day).title() == str(f"{date_time:%A}").title():
                time_slots = schdl.time_slot
                check = False
                for time_slot in time_slots.all():
                    start_hour = int(time_slot.start_time.hour)
                    end_hour = int(time_slot.end_time.hour)
                    if int(date_time.hour) >= start_hour:
                        if int(date_time.hour) < end_hour:
                            check = True
                        elif int(date_time.hour) == end_hour:
                            if date_time.minute >= time_slot.end_time.minute:
                                check = True
                    if check:
                        start_date = dt.datetime(
                            year=date_time.year, month=date_time.month,
                            day=date_time.day, hour=time_slot.start_time.hour,
                            minute=time_slot.start_time.minute
                        )
                        end_date = dt.datetime(
                            year=date_time.year, month=date_time.month,
                            day=date_time.day, hour=time_slot.end_time.hour,
                            minute=time_slot.end_time.minute
                        )
                        appointments = Appointment.objects.filter(doctor=doctor).exclude(
                            date_of_appointment__lt=start_date).exclude(
                            date_of_appointment__gt=end_date
                        )
                        if appointments.count() >= time_slot.number_of_appointments:
                            return {"validated": False, "message": "Timeslot is Fully Booked."}
                        else:
                            return {"validated": True, "message": None}
    else:
        return {"validated": False, "message": "Doctor has not created a schedule."}
    return {
        "validated": False,
        "message": "Invalid Date: Check the Doctor Appointment Schedule before booking."
    }
