from __future__ import unicode_literals

from datetime import timedelta

import sys
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import Group


# Create your models here.
from django.utils import timezone
from imagekit.models import ImageSpecField
from pilkit.processors import ResizeToFill, ResizeToFit

from mylib.image import scramble



class UserMixin(models.Model):
    last_activity = models.DateTimeField(default=timezone.now, editable=False)

    def update_last_activity(self):
        self.last_activity = timezone.now()
        self.save(update_fields=["last_activity"])

    class Meta:
        abstract = True


class MyUser(UserMixin, AbstractUser):  
    SEX = (('MALE', 'Male'), ('FEMALE', 'Female'), ('NS', 'Not Set'))
    # ROLES = ((1, 'DOCTOR'), (2, 'PATIENT'), (3, 'ADMIN'))

    role = models.ForeignKey(Group, null=True, blank=True, on_delete=models.SET_NULL)
    phone = models.CharField(max_length=50)
    image = models.ImageField("uploads", upload_to=scramble, null=True, blank=True)
    thumbnail = ImageSpecField(source='image', processors=[ResizeToFit(height=400)], format='JPEG',
        options={'quality': 80})
    confirm_code = models.IntegerField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    reset_code = models.IntegerField(null=True, blank=True)
    old_password = models.CharField(null=True, blank=True, max_length=55, editable=False)
    changed_password = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=10, default="NS", choices=SEX)
    country = models.CharField('Country', max_length=100, null=True, blank=True)
    county = models.CharField('County', max_length=100, null=True, blank=True)
    town = models.CharField('Town', max_length=100, null=True, blank=True)
    street = models.CharField('Street', max_length=200, null=True, blank=True)
    address = models.CharField('Address', max_length=200, null=True, blank=True)

    @property
    def full_name(self):
        return "{} {}".format(self.first_name, self.last_name).title()  

    class Meta:
        ordering = ('id',)


class ActivityLog(models.Model):
    user = models.ForeignKey(MyUser, null=True, blank=True, on_delete=models.SET_NULL)
    request_url = models.URLField(max_length=256)
    request_method = models.CharField(max_length=10)
    response_code = models.CharField(max_length=3)
    datetime = models.DateTimeField(default=timezone.now)
    device = models.CharField(max_length=1000, null=True, blank=True)
    browser = models.CharField(max_length=1000, null=True, blank=True)
    os = models.CharField(max_length=1000, null=True, blank=True)
    extra_data = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ('id',)


