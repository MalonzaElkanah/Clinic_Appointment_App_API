from django.contrib.auth.models import Group, Permission

from rest_framework import serializers

from client.models import MyUser


class MyUserSerializer(serializers.ModelSerializer):
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
            "username": {"required": False},
            "password": {"write_only": True, "required": True},
            "email": {"required": True},
            "last_login": {"read_only": True, "required": False},
            "verified": {"read_only": True, "required": False},
            "date_joined": {"read_only": True, "required": False},
        }

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == "password":
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


class ClientSerializer(serializers.ModelSerializer):
    role = serializers.CharField(read_only=True)

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
            "last_login",
            "verified",
            "password",
        )

        extra_kwargs = {"username": {"required": False}, "email": {"required": True}}
        depth = 1


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if MyUser.objects.filter(email=value).exists():
            return value

        raise serializers.ValidationError("user does not exist.")


class ResetPasswordserializer(serializers.Serializer):
    reset_code = serializers.IntegerField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_reset_code(self, value):
        if not MyUser.objects.filter(reset_code=value).exists():
            raise serializers.ValidationError("Reset code Invalid or Expired")
        return value


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "name", "codename"]


class GroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = "__all__"
