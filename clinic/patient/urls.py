from django.urls import path

from clinic.patient.views import ListCreatePatient, RetrieveUpdateDestroyPatient

urlpatterns=[
	path('', ListCreatePatient.as_view(), name="patient_list_create"),
	path('<int:pk>/', RetrieveUpdateDestroyPatient.as_view(), name="patient_retrieve_update"),
]