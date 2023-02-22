from django.contrib.auth.models import Group

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from client.permissions import IsOwner
from client.models import MyUser
from administrator.models import Speciality
from clinic.models import Clinic, Doctor
from clinic.serializers import ClinicSerializer, ClinicInviteDoctorSerializer

from mylib import token
from mylib.common import MySendEmail

from random import randint


class ListCreateClinic(generics.ListCreateAPIView):
    queryset = Clinic.objects.all()
    serializer_class = ClinicSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        clinic = Clinic(**serializer.validated_data, user=request.user)
        clinic.save()

        return Response(
            self.get_serializer(clinic).data
        )


class RetrieveUpdateDestroyClinic(generics.RetrieveUpdateDestroyAPIView):
    queryset = Clinic.objects.all()
    serializer_class = ClinicSerializer
    permission_classes = [IsAuthenticated, IsOwner]


class ClinicInviteDoctor(APIView):
    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self, pk, user_id):
        try:
            return Clinic.objects.get(pk=pk, user=user_id)
        except Exception as e:
            print(e)
            return None

    def post(self, request, pk, format=None):
        clinic = self.get_object(pk, request.user.id)

        if clinic is None:
            return Response(
                {"detail": "Clinic is not found!"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ClinicInviteDoctorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create invite user if he does not exist
        phone = serializer.validated_data["doctor_phone_number"]
        email = serializer.validated_data["doctor_email"]

        user = MyUser.objects.filter(email=email)

        if user.count() > 0:
            user = user[0]

            doctor = Doctor.objects.filter(user=user.id)
            if doctor.count() > 0:
                doctor = doctor[0]
            else:
                doctor = Doctor(
                    user=user,
                    speciality=Speciality.objects.all()[0]
                )
                doctor.save()

        else:
            user = MyUser(phone=phone, email=email)
            user.save()

            doctor = Doctor(
                user=user,
                speciality=Speciality.objects.all()[0]
            )
            doctor.save()

        doctor.clinic_invites.add(clinic)
        doctor.save()

        try:
            str_token = token.encode(
                email,
                expiration_seconds=(60*60*24*7)
            )

            message = f"""
            Hey Doc, \n

            You have been invited to be one of {clinic.name}'s Doctor.
            Click the following link to ACCEPT the invite:
            {reverse('doctor_accept_invite', str(pk))}?token={str_token}\n

            To CANCEL the invite click the following link:
            {reverse('doctor_reject_invite', str(pk))}?token={str_token}\n

            Good DAY.
            """
            MySendEmail(
                'Clinic Invite',
                message,
                [email]
            )
        except Exception as e:
            print(e)

            # doctor.clinic_invites.remove(self.get_object(pk))

            return Response(
                {"detail": "Error Occurred sending the invite. Try again later."}
            )

        return Response({"detail": "Invite sent successfully."})


class DoctorAcceptInvite(APIView):

    def get_object(self, pk):
        try:
            return Clinic.objects.get(pk=pk)
        except Clinic.DoesNotExist:
            return Response(
                {"detail": "Clinic is not found!"},
                status=status.HTTP_404_NOT_FOUND
            )

    def get(self, request, pk, format=None):
        str_token = request.query_params.get('token', None)

        if str_token:
            payload = token.decode(str_token)

            if 'error' in payload:
                return Response(
                    {"detail": payload['error']},
                    status=status.HTTP_400_BAD_REQUEST
                )

            email = payload['data']

            user = MyUser.objects.filter(email=email)

            if user.count() == 0:

                return Response(
                    {"detail": "User is not found!"},
                    status=status.HTTP_404_NOT_FOUND
                )

            user = user[0]
            doctor = Doctor.objects.filter(user=user.id)

            if doctor.count() == 0:

                return Response(
                    {"detail": "Doctor is not found!"},
                    status=status.HTTP_404_NOT_FOUND
                )

            doctor = doctor[0]

            clinic = self.get_object(pk)

            if clinic in list(doctor.clinic_invites.all()):
                clinic.doctors.add(doctor)
                clinic.save()
                # TODO
                # Send Notification/Email to clinic owner/admin

                doctor_role = Group.objects.filter(name="DOCTOR").first()

                # Change the user role to doctor
                if user.role.id != doctor_role.id:
                    user.role = doctor_role
                    user.save()

                # Check if its a new user
                if user.password in ['', None]:
                    # redirect if to set a new password if a new user
                    reset_code = randint(111111, 999999)

                    user.reset_code = reset_code
                    user.save()

                    try:
                        message = f"""
                        Hey Doc, \n

                        Thank you for accepting to be one of our doctors. To finish setting
                        your account, we've sent you the code: {reset_code} to set up your
                        new account password.\n {reset_code}\n

                        Good DAY.
                        """

                        MySendEmail(
                            'Password Reset Code',
                            message,
                            [email]
                        )

                    except Exception as e:
                        print(e)

                    return Response(
                        {"detail": """
                        Invite Accepted.
                        Code to setup your account has been sent to your email.
                        """}
                    )

                return Response(
                    {"detail": "Invite Accepted. Please login to finish setting your doctor profile"}
                )
            else:
                return Response(
                    {"detail": "Invite not found!"},
                    status=status.HTTP_404_NOT_FOUND
                )

        else:
            return Response(
                {"detail": "Token Arg Required."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class DoctorRejectInvite(APIView):

    def get_object(self, pk):
        try:
            return Clinic.objects.get(pk=pk)
        except Clinic.DoesNotExist:
            return Response(
                {"detail": "Clinic is not found!"},
                status=status.HTTP_404_NOT_FOUND
            )

    def get(self, request, pk, format=None):
        str_token = request.query_params.get('token', None)

        if str_token:
            payload = token.decode(str_token)

            if 'error' in payload:
                return Response(
                    {"detail": payload['error']},
                    status=status.HTTP_400_BAD_REQUEST
                )

            email = payload['data']

            user = MyUser.objects.filter(email=email)

            if user.count() == 0:

                return Response(
                    {"detail": "User is not found!"},
                    status=status.HTTP_404_NOT_FOUND
                )

            user = user[0]
            doctor = Doctor.objects.filter(user=user.id)

            if doctor.count() == 0:

                return Response(
                    {"detail": "Doctor is not found!"},
                    status=status.HTTP_404_NOT_FOUND
                )

            doctor = doctor[0]

            clinic = self.get_object(pk)

            if clinic in list(doctor.clinic_invites.all()):
                doctor.clinic_invites.remove(clinic)
                doctor.save()
                # TODO
                # Send Notification/Email to clinic owner/admin

                # Check if its a new user
                if user.password in ['', None]:
                    # delete user
                    user.delete()

            return Response(
                {"detail": "Invite Rejected!"}
            )

        else:
            return Response(
                {"detail": "Token Arg Required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
