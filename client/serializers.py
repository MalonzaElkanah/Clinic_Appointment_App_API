from django.contrib.auth.models import Group, Permission

from rest_framework import serializers
from rest_framework.response import Response

from client.models import MyUser


class PermissionSerializer(serializers.ModelSerializer):

	class Meta:
		model = Permission
		fields = ["id", "name", "codename"]


class GroupSerializer(serializers.ModelSerializer):
	permissions = PermissionSerializer(many=True)

	class Meta:
		model = Group
		fields = '__all__'
	

class ClientSerializer(serializers.ModelSerializer):
	role = GroupSerializer(many=False, read_only=True)

	class Meta:
		model = MyUser
		exclude = ("reset_code", "confirm_code", "changed_password", "user_permissions", "groups", 
			"is_staff", "last_activity", "old_password", "is_superuser", "is_active", "last_login", 
			"verified", "password",)
		
		extra_kwargs = {
			"username": {"required": False},
			"email": {"required": True}
		}


class MyUserSerializer(serializers.ModelSerializer):

	class Meta:
		model = MyUser
		exclude = ("reset_code", "confirm_code", "changed_password", "user_permissions", "groups", "is_staff",
			"last_activity", "old_password", "is_superuser", "is_active",)
		
		extra_kwargs = {
			"username": {"required": False},
			"password": {'write_only': True, 'required': True},
			"email": {"required": True}
		}

	def create(self, validated_data):
		password = validated_data.pop('password', None)
		instance = self.Meta.model(**validated_data)
		if password is not None:
		    instance.set_password(password)
		instance.save()
		return instance

	def update(self, instance, validated_data):
		for attr, value in validated_data.items():
			if attr == 'password':
				instance.set_password(value)
			else:
				setattr(instance, attr, value)
		instance.save()
		return instance

	