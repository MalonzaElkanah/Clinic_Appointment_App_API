from rest_framework import serializers

from client.models import MyUser
from clinic.models import (
    Doctor,
    Education,
    Experience,
    Award,
    Membership,
    Registration,
    DoctorSchedule,
    SocialMedia,
    AppoinmentReview,
    TimeSlot,
    Appointment,
    Reply,
    LikedReview,
    LikedReply,
)
from clinic.utils import get_roles


DOCTOR_ROLES = []
roles = get_roles("DOCTOR")
for role in roles:
    DOCTOR_ROLES.append(role)


class ClientSerializer(serializers.ModelSerializer):
    # role = serializers.HiddenField(default=DOCTOR_ROLES[0])

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
            "role": {"read_only": True, "required": False},
        }

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data, role=DOCTOR_ROLES[0])
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == "password":
                # instance.set_password(value)
                pass
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


class DoctorSerializer(serializers.ModelSerializer):

    user = ClientSerializer()

    class Meta:
        model = Doctor
        exclude = ("clinic_invites",)

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

        if password is not None:
            user.set_password(password)
            user.save()

        return Doctor.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user")

        username = user_data.get("username", None)
        email = user_data.get("email", None)
        user_data.update({"password": None})
        user_data.pop("password")

        if None in [username, email]:
            raise serializers.ValidationError("Email and Username fields are required.")

        user = self.user_update_or_create(user_data, instance=instance.user)

        instance.user = user
        instance.title = validated_data.get("title", instance.title)
        instance.biography = validated_data.get("biography", instance.biography)
        instance.pricing = validated_data.get("pricing", instance.pricing)
        instance.services = validated_data.get("services", instance.services)
        instance.specialization = validated_data.get(
            "specialization", instance.specialization
        )
        instance.speciality = validated_data.get("speciality", instance.speciality)

        instance.save()

        return instance

    def user_update_or_create(self, user_data, instance=None):
        user = None
        email = user_data.pop("email")
        username = user_data.pop("username")
        if instance is not None:
            user = MyUser.objects.filter(id=instance.id)
            user.update(role=DOCTOR_ROLES[0], **user_data)
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


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = "__all__"


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = "__all__"


class AwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Award
        fields = "__all__"


class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = "__all__"


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = "__all__"


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        # exclude = ("doctor",)
        fields = "__all__"

        extra_kwargs = {
            "doctor": {"read_only": True, "validators": []},
        }


class DoctorScheduleSerializer(serializers.ModelSerializer):
    time_slots = TimeSlotSerializer(read_only=True)

    class Meta:
        model = DoctorSchedule
        # exclude = ("doctor",)
        fields = "__all__"

        extra_kwargs = {
            "doctor": {"read_only": True, "validators": []},
        }


class SocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMedia
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppoinmentReview
        fields = "__all__"


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = "__all__"

        extra_kwargs = {
            "amount": {"read_only": True, "validators": []},
            "status": {"read_only": True, "validators": []},
            "doctor": {"read_only": True, "validators": []},
            "follow_up_appointment": {"read_only": True},
        }


class AppointmentStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        required=True, choices=[x[0] for x in Appointment.STATUS]
    )


class ReplySerializer(serializers.ModelSerializer):
    user = ClientSerializer(read_only=True)

    class Meta:
        model = Reply
        fields = "__all__"

        extra_kwargs = {
            "user": {"read_only": True, "validators": []},
        }


class LikedReviewSerializer(serializers.ModelSerializer):
    user = ClientSerializer(read_only=True)

    class Meta:
        model = LikedReview
        fields = "__all__"

        extra_kwargs = {
            "user": {"read_only": True, "validators": []},
            "appointment": {"read_only": True, "validators": []},
        }


class LikedReplySerializer(serializers.ModelSerializer):
    user = ClientSerializer(read_only=True)

    class Meta:
        model = LikedReply
        fields = "__all__"

        extra_kwargs = {
            "user": {"read_only": True, "validators": []},
        }
