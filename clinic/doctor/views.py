from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from client.permissions import IsOwnerOrReadOnly
from clinic.doctor.permissions import (
    IsOwnerDoctorOrReadOnly,
    IsOwnerDoctorOrPatientPOSTOnly,
    IsOwnerReviewOrDoctorReadOnly,
    IsOwnerReplyOrReadOnly,
)
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
    LikedReview,
    Reply,
    LikedReply,
    Patient,
)
from clinic.viewsets import CreateListRetrieveViewSet
from clinic.doctor.serializers import (
    DoctorSerializer,
    EducationSerializer,
    ExperienceSerializer,
    AwardSerializer,
    MembershipSerializer,
    RegistrationSerializer,
    DoctorScheduleSerializer,
    TimeSlotSerializer,
    SocialMediaSerializer,
    ReviewSerializer,
    AppointmentSerializer,
    AppointmentStatusSerializer,
    ReplySerializer,
    LikedReviewSerializer,
    LikedReplySerializer,
)
from clinic.utils import validate_appointment_date

from mylib.common import MyCustomException


class ListCreateDoctor(generics.ListCreateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = []

    def get_queryset(self):
        """
        Show Doctor Data to Auth Users Only
        """
        if self.request.user.is_authenticated:
            return Doctor.objects.all()

        return Doctor.objects.filter(id=0)


class RetrieveUpdateDestroyDoctor(generics.RetrieveUpdateDestroyAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


class EducationViewSet(viewsets.ModelViewSet):
    queryset = Education.objects.all()
    serializer_class = EducationSerializer
    permission_classes = [IsAuthenticated, IsOwnerDoctorOrReadOnly]

    def get_queryset(self):
        doctors = Doctor.objects.filter(id=self.kwargs["doctor_pk"])
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
        doctors = Doctor.objects.filter(id=self.kwargs["doctor_pk"])
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
        doctors = Doctor.objects.filter(id=self.kwargs["doctor_pk"])
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
        doctors = Doctor.objects.filter(id=self.kwargs["doctor_pk"])
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
        doctors = Doctor.objects.filter(id=self.kwargs["doctor_pk"])
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
        doctors = Doctor.objects.filter(id=self.kwargs["doctor_pk"])
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
        doctors = Doctor.objects.filter(id=self.kwargs["doctor_pk"])
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
        doctors = Doctor.objects.filter(id=self.kwargs["doctor_pk"])
        if doctors.count() < 1:
            raise MyCustomException("Error: Doctor not Found")
        return SocialMedia.objects.filter(doctor=doctors[0].id)

    def perform_create(self, serializer):
        doctor = Doctor.objects.filter(user=self.request.user.id)
        if doctor.count() < 1:
            raise MyCustomException("Error: You are not a Doctor")
        serializer.save(doctor=doctor[0])


class AppointmentViewSet(CreateListRetrieveViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated, IsOwnerDoctorOrPatientPOSTOnly]

    def get_queryset(self):
        doctors = Doctor.objects.filter(id=self.kwargs["doctor_pk"])
        if not doctors.exists():
            raise MyCustomException("Error: Doctor not Found", code=404)
        return Appointment.objects.filter(doctor=doctors[0].id)

    def get_object(self):
        doctors = Doctor.objects.filter(id=self.kwargs["doctor_pk"])
        if not doctors.exists():
            raise MyCustomException("Error: Doctor not Found", code=404)

        appointment = Appointment.objects.filter(
            id=self.kwargs["pk"], doctor=doctors[0].id
        )
        if not appointment.exists():
            raise MyCustomException("Error: Appointment not Found", code=404)

        return appointment[0]

    def perform_create(self, serializer):
        # Check request.user.role is patient or owner doctor
        user = self.request.user
        if user.role.name == "DOCTOR":
            doctor = Doctor.objects.filter(user=user.id)
            if doctor.count() < 1:
                raise MyCustomException("Error: Doctor does not Exist.")
            date_time = serializer.validated_data.get("date_of_appointment", None)
            if date_time is not None:
                valid_date = validate_appointment_date(doctor[0].id, date_time)
                if valid_date["validated"] is False:
                    raise MyCustomException(valid_date["message"])
            serializer.save(
                doctor=doctor[0], status="WAITING", amount=doctor[0].pricing
            )
        elif user.role.name == "PATIENT":
            patients = Patient.objects.filter(user=user.id)
            if patients.count() < 1:
                raise MyCustomException("Error: Patient does not Exist.")

            doctors = Doctor.objects.filter(id=self.kwargs["doctor_pk"])
            if doctors.count() < 1:
                raise MyCustomException("Error: Doctor not Found")
            date_time = serializer.validated_data.get("date_of_appointment", None)
            if date_time is not None:
                valid_date = validate_appointment_date(doctors[0].id, date_time)
                if valid_date["validated"] is False:
                    raise MyCustomException(valid_date["message"])
            serializer.save(
                patient=patients[0],
                doctor=doctors[0],
                status="WAITING",
                amount=doctors[0].pricing,
            )
        else:
            raise MyCustomException(
                "Error: You don't have permissions to create Appointments."
            )

    @action(detail=True, methods=["patch"])
    def update_status(self, request, pk=None, **kwargs):
        instance = self.get_object()

        if request.user.id == instance.doctor.user.id:
            if instance.status.upper() in ["CANCELED", "COMPLETED"]:
                raise MyCustomException(
                    f"Error: This appointments has been {instance.status}."
                )

            serializer = AppointmentStatusSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            status = serializer.validated_data.get("status", None)

            # Check change in status is valid
            if instance.status != status and status is not None:
                if status.upper() not in [
                    "CONFIRMED",
                    "COMPLETED",
                ]:
                    raise MyCustomException(
                        'Error: Invalid status! Status should be : "CONFIRMED" or "COMPLETED"'
                    )
                instance.status = status
                instance.save()
                # TODO
                # Notify patient change in Status

                return Response({"detail": "Status Updated"})
            else:
                raise MyCustomException("Error: Enter a valid status.")
        else:
            raise MyCustomException("Appointment Doctor Only", code=403)

    @action(detail=True, methods=["delete"])
    def cancel(self, request, pk=None, **kwargs):
        instance = self.get_object()

        if request.user.id == instance.doctor.user.id:
            if instance.status.upper() in ["CANCELED", "COMPLETED", "PAID"]:
                raise MyCustomException(
                    f"Error: This appointments has already been {instance.status}."
                )

            instance.status = "CANCELED"
            instance.save()
            # TODO
            # Notify doc change in date of appointment

            return Response({"detail": "Appointment has been Canceled"})
        else:
            raise MyCustomException("Appointment Doctor Only", code=403)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = AppoinmentReview.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsOwnerReviewOrDoctorReadOnly]

    def get_queryset(self):
        doctors = Doctor.objects.filter(id=self.kwargs["doctor_pk"])
        if doctors.count() < 1:
            raise MyCustomException("Error: Doctor not Found")
        return AppoinmentReview.objects.filter(appointment__doctor=doctors[0].id)

    def perform_create(self, serializer):
        # Check request.user.role is patient
        user = self.request.user

        patients = Patient.objects.filter(user=user.id)
        if patients.count() < 1:
            raise MyCustomException("Error: You are not a Patient!", code=403)

        doctors = Doctor.objects.filter(id=self.kwargs["doctor_pk"])
        if doctors.count() < 1:
            raise MyCustomException("Error: Doctor not Found", code=404)

        # Validate if the appoinment provided is completed
        appointment = serializer.validated_data.get("appointment", None)

        if appointment is None:
            raise MyCustomException("Error: Invalid Appointment!!")

        if (
            appointment.patient.id != patients[0].id
            or appointment.doctor.id != doctors[0].id
        ):
            raise MyCustomException("Error: Invalid Appointment!!")

        if appointment.status.upper() != "COMPLETED":
            raise MyCustomException("Error: The appointment has not been Completed!")

        serializer.save()

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def react(self, request, pk=None, **kwargs):
        instance = self.get_object()

        serializer = LikedReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recommend = serializer.validated_data.get("recommend", None)

        my_likes = LikedReview.objects.filter(user=request.user.id, review=instance.id)

        if my_likes.exists():
            like = my_likes.first()
            like.recommend = recommend
            like.save()
        else:
            like = LikedReview(user=request.user, recommend=recommend, review=instance)
            like.save()

        if recommend:
            return Response({"detail": "Review Liked"}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"detail": "Review Disliked"}, status=status.HTTP_201_CREATED
            )

    @react.mapping.delete
    def delete_react(self, request, pk=None, **kwargs):
        instance = self.get_object()

        my_likes = LikedReview.objects.filter(user=request.user.id, review=instance.id)

        if my_likes.exists():
            my_likes.delete()

        return Response({"detail": "No Reaction."}, status=status.HTTP_204_NO_CONTENT)


class ReviewReplyViewSet(viewsets.ModelViewSet):
    queryset = Reply.objects.all()
    serializer_class = ReplySerializer
    permission_classes = [IsAuthenticated, IsOwnerReplyOrReadOnly]

    def get_queryset(self):
        doctors = Doctor.objects.filter(id=self.kwargs["doctor_pk"])
        if not doctors.exists():
            raise MyCustomException("Error: Doctor not Found", code=404)

        reviews = AppoinmentReview.objects.filter(
            id=self.kwargs["review_pk"], appointment__doctor=doctors.first().id
        )
        if not reviews.exists():
            raise MyCustomException("Error: Review not Found", code=404)

        return Reply.objects.filter(review=reviews.first().id)

    def perform_create(self, serializer):
        # Check review exists
        reviews = AppoinmentReview.objects.filter(id=self.kwargs["review_pk"])
        if not reviews.exists():
            raise MyCustomException("Error: Review not Found!", code=404)

        serializer.save(user=self.request.user, review=reviews.first())

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def react(self, request, pk=None, **kwargs):
        instance = self.get_object()

        serializer = LikedReplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recommend = serializer.validated_data.get("recommend", None)

        my_likes = LikedReply.objects.filter(user=request.user.id, reply=instance.id)

        if my_likes.exists():
            like = my_likes.first()
            like.recommend = recommend
            like.save()
        else:
            like = LikedReply(user=request.user, recommend=recommend, reply=instance)
            like.save()

        if recommend:
            return Response({"detail": "Reply Liked"}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"detail": "Reply Disliked"}, status=status.HTTP_201_CREATED
            )

    @react.mapping.delete
    def delete_react(self, request, pk=None, **kwargs):
        instance = self.get_object()

        my_likes = LikedReply.objects.filter(user=request.user.id, reply=instance.id)

        if my_likes.exists():
            my_likes.delete()

        return Response({"detail": "No Reaction."}, status=status.HTTP_204_NO_CONTENT)
