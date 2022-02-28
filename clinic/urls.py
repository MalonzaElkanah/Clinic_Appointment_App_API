from django.urls import path

from clinic.views import ListCreateClinic, RetrieveUpdateDestroyClinic

urlpatterns=[
	path('', ListCreateClinic.as_view(), name="clinic_list_create"),
	path('<int:pk>/', RetrieveUpdateDestroyClinic.as_view(), name="clinic_retrieve_update"),
]