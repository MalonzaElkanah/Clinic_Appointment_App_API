from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from client.permissions import IsOwner
from clinic.models import Clinic
from clinic.serializers import ClinicSerializer

# Create your views here.

class ListCreateClinic(generics.ListCreateAPIView):
	queryset = Clinic.objects.all()
	serializer_class = ClinicSerializer
	permission_classes = [IsAuthenticated]


class RetrieveUpdateDestroyClinic(generics.RetrieveUpdateDestroyAPIView):
	queryset = Clinic.objects.all()
	serializer_class = ClinicSerializer
	permission_classes = [IsAuthenticated, IsOwner]


