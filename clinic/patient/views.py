from rest_framework import generics
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from client.permissions import IsAuthenticatedOrPOSTOnly, IsOwnerOrReadOnly
from clinic.patient.permissions import IsOwnerDoctorOrReadOnly, IsDoctorOrReadOnly, IsOwnerOrDoctor, \
IsOwnerDoctorOrIsOwnerPatient, IsOwnerPatient, IsOwnerOrDoctorReadOnly, \
DoctorReadOnlyIfAuthenticatedOrPOSTOnly
from clinic.models import Patient, Prescription, MedicalRecord, FavouriteDoctor, Appointment, Invoice, \
DoctorSchedule
from clinic.patient.serializers import PatientSerializer, PrescriptionSerializer, \
MedicalRecordSerializer, FavouriteDoctorSerializer, AppointmentSerializer, InvoiceSerializer 

from mylib.common import MyCustomException

import datetime as dt
# Create your views here.


class ListCreatePatient(generics.ListCreateAPIView):
	queryset = Patient.objects.all()
	serializer_class = PatientSerializer
	permission_classes = [DoctorReadOnlyIfAuthenticatedOrPOSTOnly]


class RetrieveUpdateDestroyPatient(generics.RetrieveUpdateDestroyAPIView):
	queryset = Patient.objects.all()
	serializer_class = PatientSerializer
	permission_classes = [IsOwnerOrDoctorReadOnly]


class PrescriptionViewSet(viewsets.ModelViewSet):
	queryset = Prescription.objects.all()
	serializer_class = PrescriptionSerializer
	permission_classes = [IsAuthenticated, IsOwnerDoctorOrReadOnly, IsDoctorOrReadOnly, IsOwnerOrDoctor]

	def get_queryset(self):
		patients = Patient.objects.filter(id=self.kwargs['patient_pk'])
		if patients.count() < 1:
			raise MyCustomException("Error: Patient not Found")
		return Prescription.objects.filter(patient=patients[0].id)

	def perform_create(self, serializer):
		patients = Patient.objects.filter(id=self.kwargs['patient_pk'])
		if patients.count() < 1:
			raise MyCustomException("Error: You are not a Patient")
		serializer.save(patient=patients[0])


class MedicalRecordViewSet(viewsets.ModelViewSet):
	queryset = MedicalRecord.objects.all()
	serializer_class = MedicalRecordSerializer
	permission_classes = [IsAuthenticated, IsOwnerDoctorOrReadOnly, IsDoctorOrReadOnly, IsOwnerOrDoctor]

	def get_queryset(self):
		patients = Patient.objects.filter(id=self.kwargs['patient_pk'])
		if patients.count() < 1:
			raise MyCustomException("Error: Patient not Found")
		return MedicalRecord.objects.filter(patient=patients[0].id)

	def perform_create(self, serializer):
		patients = Patient.objects.filter(id=self.kwargs['patient_pk'])
		if patients.count() < 1:
			raise MyCustomException("Error: You are not a Patient")
		serializer.save(patient=patients[0])


class FavouriteDoctorViewSet(viewsets.ModelViewSet):
	queryset = FavouriteDoctor.objects.all()
	serializer_class = FavouriteDoctorSerializer
	permission_classes = [IsAuthenticated, IsOwnerPatient]

	def get_queryset(self):
		patients = Patient.objects.filter(id=self.kwargs['patient_pk'])
		if patients.count() < 1:
			raise MyCustomException("Error: Patient not Found")
		return FavouriteDoctor.objects.filter(patient=patients[0].id)

	def perform_create(self, serializer):
		patients = Patient.objects.filter(id=self.kwargs['patient_pk'])
		if patients.count() < 1:
			raise MyCustomException("Error: You are not a Patient")
		serializer.save(patient=patients[0])


class AppointmentViewSet(viewsets.ModelViewSet):
	queryset = Appointment.objects.all()
	serializer_class = AppointmentSerializer
	permission_classes = [IsAuthenticated, IsOwnerPatient]

	def get_queryset(self):
		patients = Patient.objects.filter(id=self.kwargs['patient_pk'])
		if patients.count() < 1:
			raise MyCustomException("Error: Patient not Found")
		return Appointment.objects.filter(patient=patients[0].id)

	def perform_create(self, serializer):
		patients = Patient.objects.filter(id=self.kwargs['patient_pk'])
		if patients.count() < 1:
			raise MyCustomException("Error: You are not a Patient")
		date_time = serializer.validated_data.get('date_of_appointment', None)
		doctor = serializer.validated_data.get('doctor', 0)
		if date_time is not None:
			valid_date = validate_appointment_date(int(doctor.id), date_time)
			if valid_date["validated"] == False:
				raise MyCustomException(valid_date["message"])
		serializer.save(patient=patients[0], status='WAITING', amount=doctor.pricing)


class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = Invoice.objects.all()
	serializer_class = InvoiceSerializer
	permission_classes = [IsAuthenticated, IsOwnerDoctorOrIsOwnerPatient]

	def get_queryset(self):
		patients = Patient.objects.filter(id=self.kwargs['patient_pk'])
		if patients.count() < 1:
			raise MyCustomException("Error: Patient not Found")
		return Invoice.objects.filter(appointment__patient=patients[0].id)



def validate_appointment_date(doctor, date_time):
	schedules = DoctorSchedule.objects.filter(doctor=doctor)
	if schedules.count() > 0:
		today = dt.date.today()
		tomorrow = today + dt.timedelta(days=1)
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
	return {"validated": False, 
		"message": "Invalid Date: Check the Doctor Appointment Schedule before booking."}

