from django.urls import path

from client.views import (
    ListUsersAPIView,
    RetrieveDestroyUserAPIView,
    RetrieveUpdateMyProfileAPIView,
    ChangePasswordAPIView,
    ForgotPasswordAPIView,
    ResetPasswordAPIView,
    RetrieveUpdateDestroyGroupAPIView,
    ListCreateGroupAPIView,
)


urlpatterns = [
    path("", ListUsersAPIView.as_view(), name="users_list"),
    path(
        "<int:pk>/", RetrieveDestroyUserAPIView.as_view(), name="users_retrieve_destroy"
    ),
    path(
        "me/",
        RetrieveUpdateMyProfileAPIView.as_view(),
        name="myprofile_retrieve_update",
    ),
    path(
        "me/change-password/",
        ChangePasswordAPIView.as_view(),
        name="client_change_password",
    ),
    path(
        "forgot-password/",
        ForgotPasswordAPIView.as_view(),
        name="client_forgot_password",
    ),
    path(
        "reset-password/", ResetPasswordAPIView.as_view(), name="client_reset_password"
    ),
    path("groups/", ListCreateGroupAPIView.as_view(), name="groups_list_create"),
    path(
        "groups/<int:pk>/",
        RetrieveUpdateDestroyGroupAPIView.as_view(),
        name="groups_retrieve_update_destroy",
    ),
]
