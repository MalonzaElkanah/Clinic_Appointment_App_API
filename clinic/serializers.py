from rest_framework import serializers

from clinic.models import Clinic


class ClinicSerializer(serializers.ModelSerializer):

	class Meta:
		model = Clinic
		fields = '__all__'


