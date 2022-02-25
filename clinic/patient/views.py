from django.shortcuts import render

from rest_framework import generics

from client.permissions import IsAuthenticatedOrPOSTOnly
from clinic.models import Patient
from clinic.patient.serializers import PatientSerializer

# Create your views here.


class ListCreatePatient(generics.ListCreateAPIView):
	queryset = Patient.objects.all()
	serializer_class = PatientSerializer
	permission_classes = [IsAuthenticatedOrPOSTOnly]


class RetrieveUpdateDestroyPatient(generics.RetrieveUpdateDestroyAPIView):
	queryset = Patient.objects.all()
	serializer_class = PatientSerializer
	# permission_classes = [IsRoleAdmin]


