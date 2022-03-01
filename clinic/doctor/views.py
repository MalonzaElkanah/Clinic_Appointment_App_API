from rest_framework import generics
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from client.permissions import IsAuthenticatedOrPOSTOnly, IsOwnerOrReadOnly
from clinic.models import Doctor, Education, Experience, Award, Membership, Registration, \
DoctorSchedule, TimeSlot, SocialMedia, Appointment, AppoinmentReview, TimeSlot, DoctorSchedule
from clinic.doctor.serializers import DoctorSerializer, EducationSerializer, ExperienceSerializer, \
AwardSerializer, MembershipSerializer, RegistrationSerializer, DoctorScheduleSerializer, \
TimeSlotSerializer, SocialMediaSerializer, ReviewSerializer
from clinic.patient.serializers import AppointmentSerializer

from mylib.common import MyCustomException

# Create your views here.


class ListCreateDoctor(generics.ListCreateAPIView):
	queryset = Doctor.objects.all()
	serializer_class = DoctorSerializer
	permission_classes = [IsAuthenticatedOrPOSTOnly, IsOwnerOrReadOnly]


class RetrieveUpdateDestroyDoctor(generics.RetrieveUpdateDestroyAPIView):
	queryset = Doctor.objects.all()
	serializer_class = DoctorSerializer
	permission_classes = [IsOwnerOrReadOnly]


class EducationViewSet(viewsets.ModelViewSet):
	queryset = Education.objects.all()
	serializer_class = EducationSerializer
	permission_classes = [IsAuthenticated]

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
	permission_classes = [IsAuthenticated]

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
	permission_classes = [IsAuthenticated]

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
	permission_classes = [IsAuthenticated]

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
	permission_classes = [IsAuthenticated]

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
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		doctors = Doctor.objects.filter(id=self.kwargs['doctor_pk'])
		if doctors.count() < 1:
			raise MyCustomException("Error: Doctor not Found")
		return DoctorSchedule.objects.filter(doctor=doctors[0].id)

	def perform_create(self, serializer):
		doctor = Doctor.objects.filter(user=self.request.user.id)
		if doctor.count() < 1:
			raise MyCustomException("Error: You are not a Doctor")
		serializer.save(doctor=doctor[0])


class TimeSlotViewSet(viewsets.ModelViewSet):
	queryset = TimeSlot.objects.all()
	serializer_class = TimeSlotSerializer
	permission_classes = [IsAuthenticated]

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
	permission_classes = [IsAuthenticated]

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
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		doctors = Doctor.objects.filter(id=self.kwargs['doctor_pk'])
		if doctors.count() < 1:
			raise MyCustomException("Error: Doctor not Found")
		return Appointment.objects.filter(doctor=doctors[0].id)

	def perform_create(self, serializer):
		doctor = Doctor.objects.filter(user=self.request.user.id)
		if doctor.count() < 1:
			raise MyCustomException("Error: You are not a Doctor")
		serializer.save(doctor=doctor[0])


class ReviewViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = AppoinmentReview.objects.all()
	serializer_class = ReviewSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		doctors = Doctor.objects.filter(id=self.kwargs['doctor_pk'])
		if doctors.count() < 1:
			raise MyCustomException("Error: Doctor not Found")
		return AppoinmentReview.objects.filter(appointment__doctor=doctors[0].id)

