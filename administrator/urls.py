from django.urls import path, include

from administrator.views import (
    ListCreateSpeciality,
    RetrieveUpdateDestroySpeciality,
    ListCreateAdminInviteAPIView,
    RetrieveDestroyAdminInviteAPIView,
    AcceptAdminInviteAPIView,
    RejectAdminInviteAPIView,
)


urlpatterns = [
    path("speciality/", ListCreateSpeciality.as_view(), name="speciality_list_create"),
    path(
        "speciality/<int:pk>/",
        RetrieveUpdateDestroySpeciality.as_view(),
        name="speciality_retrieve_update_destroy",
    ),
    path(
        "invites/",
        ListCreateAdminInviteAPIView.as_view(),
        name="admin_invites_list_create",
    ),
    path(
        "invites/<int:pk>/",
        RetrieveDestroyAdminInviteAPIView.as_view(),
        name="admin_invites_retrieve_destroy",
    ),
    path(
        "invites/<int:pk>/accept/",
        AcceptAdminInviteAPIView.as_view(),
        name="admin_invites_accept",
    ),
    path(
        "invites/<int:pk>/reject/",
        RejectAdminInviteAPIView.as_view(),
        name="admin_invites_reject",
    ),
    path("logs/", include("client.activity_logs.urls")),
]
