from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings

from drf_autodocs.views import TreeView

urlpatterns_v1 = [
    path('users/', include('client.urls')),
    path('patients/', include('clinic.patient.urls')),
    path('doctors/', include('clinic.doctor.urls')),
    path('admin/', include('administrator.urls')),
    path('clinics/', include('clinic.urls')),
]

# versions from the Apis(v1,v2)
apiversions_urlsparterns = [
    path('v1/', include(urlpatterns_v1)),
]

urlpatterns = [
    path('apiauth/', include('rest_framework.urls')), 
    path('api/', include(apiversions_urlsparterns)),
    path('', TreeView.as_view(), name='api-tree'),
]

urlpatterns += staticfiles_urlpatterns()

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)