from django.urls import path, include

from rest_framework.routers import DefaultRouter

from clinic.patient import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"prescription", views.PrescriptionViewSet)
router.register(r"medical-record", views.MedicalRecordViewSet)
router.register(r"appointments", views.AppointmentViewSet)
router.register(r"invoices", views.InvoiceViewSet)

app_name = "patient"

urlpatterns = [
    path("", views.ListCreatePatient.as_view(), name="patient_list_create"),
    path(
        "<int:pk>/",
        views.RetrieveUpdateDestroyPatient.as_view(),
        name="patient_retrieve_update",
    ),
    path(
        "favourite-doctor/",
        views.ListCreateFavouriteDoctor.as_view(),
        name="favourite-doctor_list_create",
    ),
    path(
        "favourite-doctor/<int:pk>/",
        views.DestroyFavouriteDoctor.as_view(),
        name="favourite-doctor_destroy",
    ),
    path("<int:patient_pk>/", include(router.urls)),
]
