from django.urls import path

from clinic.views import (
    ListCreateClinic, RetrieveUpdateDestroyClinic,
    ClinicInviteDoctor, DoctorAcceptInvite, DoctorRejectInvite
)


urlpatterns = [
    path('', ListCreateClinic.as_view(), name="clinic_list_create"),
    path('<int:pk>/', RetrieveUpdateDestroyClinic.as_view(), name="clinic_retrieve_update"),
    path('<int:pk>/invite-doctor/', ClinicInviteDoctor.as_view(), name="clinic_invite_doctor"),
    path('<int:pk>/accept-invite/', DoctorAcceptInvite.as_view(), name="doctor_accept_invite"),
    path('<int:pk>/reject-invite/', DoctorRejectInvite.as_view(), name="doctor_reject_invite"),
]
