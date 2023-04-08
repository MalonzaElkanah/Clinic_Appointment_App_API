from django.contrib.auth.models import Group

from rest_framework import serializers

from client.models import MyUser
from clinic.models import (
    Patient,
    Prescription,
    MedicalRecord,
    FavouriteDoctor,
    Appointment,
    Invoice,
    Bill,
)
from clinic.utils import get_roles


PATIENT_ROLES = []

roles = get_roles("PATIENT")

for role in roles:
    PATIENT_ROLES.append(role.id)


class ClientSerializer(serializers.ModelSerializer):
    role = serializers.HiddenField(default=PATIENT_ROLES[0])

    class Meta:
        model = MyUser
        exclude = (
            "reset_code",
            "confirm_code",
            "changed_password",
            "user_permissions",
            "groups",
            "is_staff",
            "last_activity",
            "old_password",
            "is_superuser",
            "is_active",
        )

        extra_kwargs = {
            "username": {"required": True, "validators": []},
            "password": {"write_only": True, "required": False, "validators": []},
            "email": {"required": True, "validators": []},
            "last_login": {"read_only": True, "required": False},
            "verified": {"read_only": True, "required": False},
            "date_joined": {"read_only": True, "required": False},
        }

    def validate(self, data):
        """
        Check that User Role is PATIENT.
        """
        if int(data["role"]) not in PATIENT_ROLES:
            raise serializers.ValidationError("The User role must be PATIENT")
        return data


class PatientSerializer(serializers.ModelSerializer):

    user = ClientSerializer()

    class Meta:
        model = Patient
        fields = "__all__"

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        username = user_data.get("username", None)
        email = user_data.get("email", None)
        password = user_data.get("password", None)
        if None in [username, email, password]:
            raise serializers.ValidationError(
                "Email, Username and Password fields are required."
            )
        user = self.user_update_or_create(user_data)
        return Patient.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        # serializer = CommentSerializer(comment, data=data)
        user_data = validated_data.pop("user")
        username = user_data.get("username", None)
        email = user_data.get("email", None)
        user_data.update({"password": None})
        user_data.pop("password")
        if None in [username, email]:
            raise serializers.ValidationError("Email and Username fields are required.")
        user = self.user_update_or_create(user_data, instance=instance.user)
        instance.user = user
        instance.blood_group = validated_data.get("blood_group", instance.blood_group)
        instance.save()
        return instance

    def user_update_or_create(self, user_data, instance=None):
        role_data = user_data.pop("role")
        groups = Group.objects.filter(id=int(role_data))
        group = None
        if groups.count() > 0:
            group = groups[0]

        user = None
        email = user_data.pop("email")
        username = user_data.pop("username")
        if instance is not None:
            user = MyUser.objects.filter(id=instance.id)
            user.update(role=group, **user_data)
            user = MyUser.objects.get(id=instance.id)
        else:
            users = MyUser.objects.filter(username=username)
            if users.count() > 0:
                raise serializers.ValidationError("Username already Exists.")

            users = MyUser.objects.filter(email=email)
            if users.count() > 0:
                raise serializers.ValidationError("Email already Exists.")

            defaults = {"email": email, "username": username}
            user, created = users.get_or_create(**user_data, defaults=defaults)

        return user


class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = "__all__"


class MedicalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = "__all__"


class FavouriteDoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavouriteDoctor
        fields = "__all__"


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = "__all__"

        extra_kwargs = {
            "amount": {"read_only": True, "validators": []},
            # "status": {'read_only': True, 'validators': []},
            # "follow_up_appointment": {'read_only': True}
        }


class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = "__all__"


class InvoiceSerializer(serializers.ModelSerializer):
    bills = BillSerializer(read_only=True, many=True)

    class Meta:
        model = Invoice
        fields = "__all__"


class AppointmentRescheduleSerializer(serializers.Serializer):
    date_of_appointment = serializers.DateTimeField(required=True)
