from django.urls import path

from client.views import ListCreateUser, ListCreateGroup, RetrieveUpdateDestroyUser, \
RetrieveUpdateDestroyGroup, RetrieveUpdateClient

urlpatterns=[
	path('', ListCreateUser.as_view(), name="users_list_create"),
	path('me/', RetrieveUpdateClient.as_view(), name="client_retrieve_update"),
	path('<int:pk>/', RetrieveUpdateDestroyUser.as_view(), name="users_retrieve_update_destroy"),
	path('groups/', ListCreateGroup.as_view(), name="groups_list_create"),
	path('groups/<int:pk>/', RetrieveUpdateDestroyGroup.as_view(), name="groups_retrieve_update_destroy"),
]