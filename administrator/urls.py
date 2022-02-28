from django.urls import path

from administrator.views import ListCreateSpeciality, RetrieveUpdateDestroySpeciality

urlpatterns=[
	path('speciality/', ListCreateSpeciality.as_view(), name="speciality_list_create"),
	path('speciality/<int:pk>/', RetrieveUpdateDestroySpeciality.as_view(), name="speciality_retrieve_update"),
]