from django.contrib.auth.models import Group
from django.db.models import Q

from rest_framework import serializers

from client.models import MyUser
from clinic.models import Doctor, Education, Experience, Award, Membership, Registration, \
DoctorSchedule, TimeSlot, SocialMedia
from client.serializers import MyUserSerializer
from mylib.common import MyCustomException

DOCTOR_ROLES = []
roles = Group.objects.filter(name="DOCTOR")
for role in roles:
	DOCTOR_ROLES.append(role.id)


class ClientSerializer(serializers.ModelSerializer):
	role = serializers.HiddenField(default=DOCTOR_ROLES[0])

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
				# instance.set_password(value)
				pass
			else:
				setattr(instance, attr, value)
		instance.save()
		return instance

	def validate(self, data):
		"""
		Check that User Role is PATIENT.
		"""
		if int(data['role']) not in DOCTOR_ROLES:
			raise serializers.ValidationError("The User role must be DOCTOR")
		return data



class DoctorSerializer(serializers.ModelSerializer):

	user = ClientSerializer()

	class Meta:
		model = Doctor
		fields = "__all__"

	def create(self, validated_data):
		user_data = validated_data.pop('user')
		username = user_data.get('username', None)
		email = user_data.get('email', None)
		password = user_data.get('password', None)
		if None in [username, email, password]: 
			raise serializers.ValidationError("Email, Username and Password fields are required.")
		user = self.user_update_or_create(user_data)
		return Doctor.objects.create(user=user, **validated_data)			

	def update(self, instance, validated_data):
		# serializer = CommentSerializer(comment, data=data)
		user_data = validated_data.pop('user')
		username = user_data.get('username', None)
		email = user_data.get('email', None)
		user_data.update({'password': None})
		password = user_data.pop('password')
		if None in [username, email]: 
			raise serializers.ValidationError("Email and Username fields are required.")
		user = self.user_update_or_create(user_data, instance=instance.user)
		instance.user = user
		# title, biography, pricing, services, specialization, speciality
		instance.title = validated_data.get('title', instance.title)
		instance.biography = validated_data.get('biography', instance.biography)
		instance.pricing = validated_data.get('pricing', instance.pricing)
		instance.services = validated_data.get('services', instance.services)
		instance.specialization = validated_data.get('specialization', instance.specialization)
		instance.speciality = validated_data.get('speciality', instance.speciality)
		instance.save()
		return instance

	def user_update_or_create(self, user_data, instance=None):
		role_data = user_data.pop('role')
		groups = Group.objects.filter(id=int(role_data))
		group = None
		if groups.count()>0:
			group = groups[0]

		user = None
		email = user_data.pop('email')
		username = user_data.pop('username')
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

			defaults={"email": email, "username": username}
			user, created = users.get_or_create(**user_data, defaults=defaults)
			
		return user


class EducationSerializer(serializers.ModelSerializer):

	class Meta:
		model = Education
		fields = '__all__'


class ExperienceSerializer(serializers.ModelSerializer):

	class Meta:
		model = Experience
		fields = '__all__'


class AwardSerializer(serializers.ModelSerializer):

	class Meta:
		model = Award
		fields = '__all__'


class MembershipSerializer(serializers.ModelSerializer):

	class Meta:
		model = Membership
		fields = '__all__'


class RegistrationSerializer(serializers.ModelSerializer):

	class Meta:
		model = Registration
		fields = '__all__'


class DoctorScheduleSerializer(serializers.ModelSerializer):

	class Meta:
		model = DoctorSchedule
		fields = '__all__'


class TimeSlotSerializer(serializers.ModelSerializer):

	class Meta:
		model = TimeSlot
		fields = '__all__'


class SocialMediaSerializer(serializers.ModelSerializer):

	class Meta:
		model = SocialMedia
		fields = '__all__'

