from django.contrib.auth.models import Group

from rest_framework import serializers

from client.models import MyUser
from clinic.models import Patient
from client.serializers import MyUserSerializer
from mylib.common import MyCustomException

PATIENT_ROLES = []
roles = Group.objects.filter(name="PATIENT")
for role in roles:
	PATIENT_ROLES.append(role.id)


class ClientSerializer(serializers.ModelSerializer):
	role = serializers.HiddenField(default=PATIENT_ROLES[0])

	class Meta:
		model = MyUser
		exclude = ("reset_code", "confirm_code", "changed_password", "user_permissions", "groups", 
			"is_staff", "last_activity", "old_password", "is_superuser", "is_active",)
		
		extra_kwargs = {
			"username": {"required": True, 'validators': []},
			"password": {'write_only': True, 'required': False, 'validators': []},
			"email": {"required": True, 'validators': []},
			"last_login": {'read_only': True, 'required': False},
			"verified": {'read_only': True, 'required': False},
			"date_joined": {'read_only': True, 'required': False},
		}

	def validate(self, data):
		"""
		Check that User Role is PATIENT.
		"""
		if int(data['role']) not in PATIENT_ROLES:
			raise serializers.ValidationError("The User role must be PATIENT")
		return data



class PatientSerializer(serializers.ModelSerializer):

	user = ClientSerializer()

	class Meta:
		model = Patient
		fields = "__all__"

	def create(self, validated_data):
		user_data = validated_data.pop('user')
		username = user_data.get('username', None)
		email = user_data.get('email', None)
		password = user_data.get('password', None)
		if None in [username, email, password]: 
			raise serializers.ValidationError("Email, Username and Password fields are required.")
		user = self.user_update_or_create(user_data)
		return Patient.objects.create(user=user, **validated_data)			

	def update(self, instance, validated_data):
		# serializer = CommentSerializer(comment, data=data)
		user_data = validated_data.pop('user')
		username = user_data.get('username', None)
		email = user_data.get('email', None)
		user_data.update({'password': None})
		password = user_data.pop('password')
		if None in [username, email]: 
			raise serializers.ValidationError("Email and Username fields are required.")
		user = self.user_update_or_create(user_data)
		instance.blood_group = validated_data.get('blood_group', instance.blood_group)
		instance.save()
		return instance

	def user_update_or_create(self, user_data):
		role_data = user_data.pop('role')
		group = Group.objects.filter(id=int(role_data))
		if group.count()>0:
			group = group[0]
		else:
			group = None
		users1 = MyUser.objects.filter(username = user_data.get('username'))
		users2 = MyUser.objects.filter(email = user_data.get('email'))
		user = None
		if users1.count() > 0 or users2.count() > 0: 
			user = MyUser.objects.update(role=group, **user_data)
		else:
			user = MyUser.objects.create(role=group, **user_data)
		return user
