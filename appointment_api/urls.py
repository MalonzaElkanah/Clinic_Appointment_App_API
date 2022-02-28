from django.contrib import admin
from django.urls import path, include

from drf_autodocs.views import TreeView

urlpatterns = [
    path('apiauth/', include('rest_framework.urls')),
    path('users/', include('client.urls')),
    path('patients/', include('clinic.patient.urls')),
    path('doctors/', include('clinic.doctor.urls')),
    path('doctors/', include('clinic.doctor.urls')),
    path('clinics/', include('clinic.urls')),

    path('', TreeView.as_view(), name='api-tree'),
]
