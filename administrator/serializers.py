from rest_framework import serializers

from administrator.models import Speciality


class SpecialitySerializer(serializers.ModelSerializer):

	class Meta:
		model = Speciality
		fields = "__all__"


