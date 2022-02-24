from django.contrib.auth.models import Group

from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from client.permissions import IsRoleAdmin, IsAuthenticatedOrPOSTOnly
from client.models import MyUser
from client.serializers import MyUserSerializer, GroupSerializer, ClientSerializer, ChangePasswordSerializer, \
    ForgotPasswordSerializer, ResetPasswordserializer
from mylib.common import MySendEmail, MyCustomException

from random import randint
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


class ChangePasswordAPiView(APIView):
    permission_classes = [IsAuthenticated, ]

    def put(self, request, format=None):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.confirm_old_password(serializer)
        self.request.user.set_password(serializer.validated_data.get("new_password"))
        self.request.user.changed_password = True
        self.request.user.save()
        return Response({"detail": "Password successfully changed."})

    def confirm_old_password(self, serializer):
        old_password = serializer.validated_data.get("old_password")
        valid = self.request.user.check_password(old_password)
        if not valid:
            raise MyCustomException("Wrong old password provided.")
        return True


class ForgotPasswordView(APIView):

    def post(self, request, format=None):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        user = MyUser.objects.get(username=email)
        cls = list(MyUser.objects.filter(id=user.id))
        if not len(cls) > 0: raise MyCustomException("No  account associated with email.")
        reset_code = randint(111111, 999999)
        cls[0].reset_code = reset_code
        cls[0].save()
        name = user.first_name
        try:
            data = {"name": name, "reset_code": reset_code}
            MySendEmail('Password Reset Code', "forgot.html", data, [email])
            return Response({"detail": "Reset code sent successfully."})
        except Exception as e:
            print(e)
            return Response({"detail": "Failed to send email."})


class ResetPasswordView(generics.UpdateAPIView):
    serializer_class = ResetPasswordserializer
    model = MyUser

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cls = list(MyUser.objects.filter(reset_code=serializer.validated_data.get("reset_code")))
        if not len(cls) > 0: raise MyCustomException("User not Found")
        self.object = cls[0].id
        new_password = serializer.data.get("new_password")
        cls[0].set_password(new_password)
        cls[0].save()
        cls[0].reset_code = None
        cls[0].save()
        return Response({"detail": "Password reset successful."}, status=status.HTTP_200_OK)
