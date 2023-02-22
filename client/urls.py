from django.urls import path

from client.views import (
    ListCreateUser, ListCreateGroup, RetrieveUpdateDestroyUser,
    RetrieveUpdateDestroyGroup, RetrieveUpdateClient, ChangePasswordAPiView,
    ForgotPasswordView, ResetPasswordView
)


urlpatterns = [
    path('', ListCreateUser.as_view(), name="users_list_create"),
    path('me/', RetrieveUpdateClient.as_view(), name="client_retrieve_update"),
    path('me/change-password/', ChangePasswordAPiView.as_view(), name="clients_change_password"),
    path('forgot-password/', ForgotPasswordView.as_view(), name="clients_forgot_password"),
    path('reset-password/', ResetPasswordView.as_view(), name="clients_reset_password"),
    path('<int:pk>/', RetrieveUpdateDestroyUser.as_view(), name="users_retrieve_update_destroy"),
    path('groups/', ListCreateGroup.as_view(), name="groups_list_create"),
    path('groups/<int:pk>/', RetrieveUpdateDestroyGroup.as_view(), name="groups_retrieve_update_destroy"),
]
