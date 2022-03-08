from rest_framework import serializers

from client.models import ActivityLog
from client.serializers import MyUserSerializer


class ActivityLogSerializer(serializers.ModelSerializer):
	user=MyUserSerializer(read_only=True)

	class Meta:
		model=ActivityLog
		fields=("__all__")


class ExportActivityLogSerializer(serializers.ModelSerializer):
	user=serializers.StringRelatedField(read_only=True)
	
	class Meta:
		model=ActivityLog
		fields=("__all__")
