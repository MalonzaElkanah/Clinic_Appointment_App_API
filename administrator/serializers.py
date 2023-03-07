from rest_framework import serializers

from administrator.models import Speciality, AdminInvite


class SpecialitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Speciality
        fields = "__all__"


class AdminInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminInvite
        fields = "__all__"

        extra_kwargs = {
            "invite_by": {"read_only": True},
            "invite_user": {"read_only": True},
            "invite_date": {"read_only": True},
            "status": {"read_only": True},
        }
