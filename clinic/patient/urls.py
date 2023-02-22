from django.urls import path, include

from rest_framework.routers import DefaultRouter

from clinic.patient import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'prescription', views.PrescriptionViewSet)
router.register(r'medical-record', views.MedicalRecordViewSet)
router.register(r'favourite-doctor', views.FavouriteDoctorViewSet)
router.register(r'appointments', views.AppointmentViewSet)
router.register(r'invoices', views.InvoiceViewSet)

urlpatterns = [
    path('', views.ListCreatePatient.as_view(), name="patient_list_create"),
    path('<int:pk>/', views.RetrieveUpdateDestroyPatient.as_view(), name="patient_retrieve_update"),
    path('<int:patient_pk>/', include(router.urls)),
]
