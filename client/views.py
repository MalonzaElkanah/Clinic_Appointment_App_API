from django.contrib.auth.models import Group

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from client.permissions import IsRoleAdmin
from client.models import MyUser
from client.serializers import (
    MyUserSerializer,
    GroupSerializer,
    ClientSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ResetPasswordserializer,
)
from mylib.common import MySendEmail, MyCustomException

from random import randint

# Create your views here.


class ListUsersAPIView(generics.ListAPIView):
    queryset = MyUser.objects.all()
    serializer_class = MyUserSerializer

    def get_queryset(self):
        """
        Show User Data to ADMIN Only or OWNER
        """
        if self.request.user.is_authenticated:
            if self.request.user.role.name == "ADMIN":
                return MyUser.objects.all()
            else:
                return MyUser.objects.filter(id=self.request.user.id)

        return MyUser.objects.filter(id=0)


class RetrieveDestroyUserAPIView(generics.RetrieveDestroyAPIView):
    queryset = MyUser.objects.all()
    serializer_class = MyUserSerializer
    permission_classes = [IsAuthenticated, IsRoleAdmin]


class RetrieveUpdateMyProfileAPIView(generics.RetrieveUpdateAPIView):
    queryset = MyUser.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def get_object(self):
        return MyUser.objects.get(id=self.request.user.id)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)

        instance = self.get_object()

        # No Email Updates: requires verification
        data = request.data
        data.update({"email": instance.email})

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class ChangePasswordAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

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


class ForgotPasswordAPIView(APIView):
    def post(self, request, format=None):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        users = MyUser.objects.filter(email=email)

        if users.count() == 0:
            raise MyCustomException("No account associated with email.")

        reset_code = randint(111111, 999999)

        user = users[0]
        user.reset_code = reset_code
        user.save()

        name = user.first_name

        try:
            message = f"""
            Hey {name}, \n
            We've sent you the code: {reset_code} to reset your password.\n
            {reset_code}\n
            Good DAY.
            """

            MySendEmail("Password Reset Code", message, [email])

            return Response(
                {"detail": "Reset code sent successfully."}, status=status.HTTP_200_OK
            )

        except Exception as e:
            print(e)

            return Response(
                {"detail": "Failed to send email."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ResetPasswordAPIView(generics.UpdateAPIView):
    serializer_class = ResetPasswordserializer
    model = MyUser

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cls = list(
            MyUser.objects.filter(
                reset_code=serializer.validated_data.get("reset_code")
            )
        )

        if not len(cls) > 0:
            raise MyCustomException("User not Found")

        self.object = cls[0].id
        new_password = serializer.data.get("new_password")

        cls[0].set_password(new_password)
        cls[0].reset_code = None
        cls[0].save()

        return Response(
            {"detail": "Password reset successful."}, status=status.HTTP_200_OK
        )


class ListCreateGroupAPIView(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, IsRoleAdmin]


class RetrieveUpdateDestroyGroupAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, IsRoleAdmin]
