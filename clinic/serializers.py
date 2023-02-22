from rest_framework import serializers

from clinic.models import Clinic


class ClinicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Clinic
        fields = '__all__'

        extra_kwargs = {
            "user": {"read_only": True},
            "doctors": {'read_only': True}
        }


class ClinicInviteDoctorSerializer(serializers.Serializer):
    doctor_email = serializers.CharField(required=True)
    doctor_phone_number = serializers.CharField(required=True)
