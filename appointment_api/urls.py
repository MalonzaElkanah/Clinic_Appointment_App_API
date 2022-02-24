from django.contrib import admin
from django.urls import path, include

from drf_autodocs.views import TreeView

urlpatterns = [
    path('apiauth/', include('rest_framework.urls')),
    path('users/', include('client.urls')),

    path('', TreeView.as_view(), name='api-tree'),
]
