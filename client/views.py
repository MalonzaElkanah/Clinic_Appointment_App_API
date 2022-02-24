from django.contrib.auth.models import Group

from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from client.models import MyUser
from client.serializers import MyUserSerializer, GroupSerializer, ClientSerializer
from client.permissions import IsRoleAdmin, IsAuthenticatedOrPOSTOnly

# Create your views here.


class ListCreateUser(generics.ListCreateAPIView):
	queryset = MyUser.objects.all()
	serializer_class = MyUserSerializer
	permission_classes = [IsAuthenticatedOrPOSTOnly]


class RetrieveUpdateDestroyUser(generics.RetrieveUpdateDestroyAPIView):
	queryset = MyUser.objects.all()
	serializer_class = MyUserSerializer
	permission_classes = [IsRoleAdmin]


class RetrieveUpdateClient(generics.RetrieveUpdateAPIView):
    queryset = MyUser.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated, ]

    def get_object(self):
        return MyUser.objects.get(id=self.request.user.id)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=self.request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class ListCreateGroup(generics.ListCreateAPIView):
	queryset = Group.objects.all()
	serializer_class = GroupSerializer
	permission_classes = [IsRoleAdmin]


class RetrieveUpdateDestroyGroup(generics.RetrieveUpdateDestroyAPIView):
	queryset = Group.objects.all()
	serializer_class = GroupSerializer
	permission_classes = [IsRoleAdmin]

