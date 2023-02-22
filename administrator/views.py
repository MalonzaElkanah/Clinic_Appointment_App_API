from rest_framework import generics

from client.permissions import IsRoleAdmin
from administrator.models import Speciality
from administrator.serializers import SpecialitySerializer

# Create your views here.


class ListCreateSpeciality(generics.ListCreateAPIView):
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer
    permission_classes = [IsRoleAdmin]


class RetrieveUpdateDestroySpeciality(generics.RetrieveUpdateDestroyAPIView):
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer
    permission_classes = [IsRoleAdmin]
