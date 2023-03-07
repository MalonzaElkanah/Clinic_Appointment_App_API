from django.urls import reverse
from django.contrib.auth.models import Group

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from client.permissions import IsRoleAdmin
from client.models import MyUser
from administrator.permissions import IsRoleAdminOrReadOnly
from administrator.models import Speciality, AdminInvite
from administrator.serializers import (
    SpecialitySerializer,
    AdminInviteSerializer,
)

from mylib import token
from mylib.common import MySendEmail

from random import randint


class ListCreateSpeciality(generics.ListCreateAPIView):
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer
    permission_classes = [IsRoleAdminOrReadOnly]


class RetrieveUpdateDestroySpeciality(generics.RetrieveUpdateDestroyAPIView):
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer
    permission_classes = [IsAuthenticated, IsRoleAdmin]


class ListCreateAdminInviteAPIView(generics.ListCreateAPIView):
    """
    An APIView that admin can List all invites or invite a new admin user.
    """

    queryset = AdminInvite.objects.all()
    serializer_class = AdminInviteSerializer
    permission_classes = [IsAuthenticated, IsRoleAdmin]

    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]
        email = serializer.validated_data["email"]

        # Check if invited user exists
        user = MyUser.objects.filter(email=email)

        if user.count() > 0:
            user = user[0]

            # Check if the user is an admin
            if user.role == "ADMIN":
                return Response(
                    {"detail": "Error: User Invited is already an admin."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Check previous Invites
        invites = AdminInvite.objects.filter(email=email)

        if invites.count() > 0:
            invite = invites[0]

        else:
            # Create Invite
            invite = AdminInvite(
                invite_by=request.user, email=email, phone_number=phone_number
            )
            invite.save()

            invite = AdminInvite.objects.get(email=email)

        try:
            str_token = token.encode(email, expiration_seconds=(60 * 60 * 24 * 7))

            message = f"""
            Hey Doc, \n

            You have been invited to be an Administrator for CAS.
            Click the following link to ACCEPT the invite:
            {reverse('admin_invites_accept', str(invite.id))}?token={str_token}\n

            To CANCEL the invite click the following link:
            {reverse('admin_invites_reject', str(invite.id))}?token={str_token}\n

            Good DAY.
            """
            MySendEmail("Clinic Invite", message, [email])
        except Exception as e:
            print(e)

            # invite.status = "NOT_SENT"
            # invite.save()

            # return Response(
            #    {"detail": "Error Occurred sending the invite. Try again later."},
            #    status=status.HTTP_500_INTERNAL_SERVER_ERROR
            # )

        return Response(
            {"detail": "Invite sent successfully."}, status=status.HTTP_201_CREATED
        )


class RetrieveDestroyAdminInviteAPIView(generics.RetrieveDestroyAPIView):
    queryset = AdminInvite.objects.all()
    serializer_class = AdminInviteSerializer
    permission_classes = [IsAuthenticated, IsRoleAdmin]


class AcceptAdminInviteAPIView(APIView):
    """
    An APIView that admin can List all invites or invite a new admin user.
    """

    def get_object(self, pk):
        try:
            return AdminInvite.objects.get(pk=pk)
        except AdminInvite.DoesNotExist:
            return Response(
                {"detail": "Invite is not found!"}, status=status.HTTP_404_NOT_FOUND
            )

    def get(self, request, pk, format=None):
        str_token = request.query_params.get("token", None)

        if str_token:
            payload = token.decode(str_token)

            if "error" in payload:
                return Response(
                    {"detail": payload["error"]}, status=status.HTTP_400_BAD_REQUEST
                )

            email = payload["data"]

            request_invites = AdminInvite.objects.filter(email=email)

            if request_invites.count() == 0:

                return Response(
                    {"detail": "Invite is not found!"}, status=status.HTTP_404_NOT_FOUND
                )

            invite = self.get_object(pk)

            if invite in list(request_invites):
                # Create or Update user with admin role
                admin_role = Group.objects.filter(name="ADMIN").first()

                user = MyUser.objects.filter(email=email)

                if user.count() > 0:
                    user = user[0]

                    if user.role.id != admin_role.id:
                        user.role = admin_role
                        user.save()
                else:
                    user = MyUser(
                        phone=invite.phone_number, email=invite.email, role=admin_role
                    )

                # Update invite status
                invite.status = "ACCEPTED"
                invite.save()

                # Check if its a new user
                if user.password in ["", None]:
                    # redirect to set a new password if a new user
                    reset_code = randint(111111, 999999)

                    user.reset_code = reset_code
                    user.save()

                    try:
                        message = f"""
                        Hey Doc, \n

                        Thank you for accepting to be an admin. To finish setting
                        your account, we've sent you the code: {reset_code} to set up your
                        new account password.\n {reset_code}\n

                        Good DAY.
                        """

                        MySendEmail("Password Reset Code", message, [email])

                    except Exception as e:
                        print(e)

                    # TODO
                    # Send Notification/Email to invited_by admin

                    return Response(
                        {
                            "detail": "Invite Accepted. Code to setup your account has been sent to your email."
                        }
                    )

                return Response({"detail": "Invite Accepted."})
            else:
                return Response(
                    {"detail": "Invite not found!"}, status=status.HTTP_404_NOT_FOUND
                )

        else:
            return Response(
                {"detail": "Token Arg Required."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class RejectAdminInviteAPIView(APIView):
    def get_object(self, pk):
        try:
            return AdminInvite.objects.get(pk=pk)
        except AdminInvite.DoesNotExist:
            return Response(
                {"detail": "Invite is not found!"}, status=status.HTTP_404_NOT_FOUND
            )

    def get(self, request, pk, format=None):
        str_token = request.query_params.get("token", None)

        if str_token:
            payload = token.decode(str_token)

            if "error" in payload:
                return Response(
                    {"detail": payload["error"]}, status=status.HTTP_400_BAD_REQUEST
                )

            email = payload["data"]

            request_invites = AdminInvite.objects.filter(email=email)

            if request_invites.count() == 0:

                return Response(
                    {"detail": "Invite not found!"}, status=status.HTTP_404_NOT_FOUND
                )

            invite = self.get_object(pk)

            if invite in list(request_invites):
                invite.status = "REJECTED"
                invite.save()
                # TODO
                # Send Notification/Email to invited_by admin

            return Response({"detail": "Invite Rejected!"})

        else:
            return Response(
                {"detail": "Token Arg Required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
