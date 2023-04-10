from django.db import models
from django.utils import timezone

from client.models import MyUser


class Speciality(models.Model):
    class Meta:
        ordering = ["id"]

    name = models.CharField("Name", max_length=100, unique=True)

    def __str__(self):
        return self.name


class AdminInvite(models.Model):
    class Meta:
        ordering = ["id"]

    invite_by = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    invite_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, default="SENT")

    def __str__(self):
        return f"{self.status}<{self.email}>"

    @property
    def invited_user(self):
        users = MyUser.objects.filter(email=self.email)

        if users.count() > 0:
            return users[0]

        return None
