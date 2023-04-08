from django.contrib.auth.models import Group

from client.models import MyUser

import random
import string


def create_default_roles():
    """
    Create admin, patient and doctor roles
    """

    Group.objects.get_or_create(name="ADMIN")
    Group.objects.get_or_create(name="PATIENT")
    Group.objects.get_or_create(name="DOCTOR")


def create_role(role_name):
    """
    Create or return role from role_name provided
    """

    role, created = Group.objects.get_or_create(name=role_name)

    return role


def create_user(
    name="".join([random.choice(string.ascii_letters) for x in range(7)]),
    role="PATIENT",
    enforce_new=True,
):
    """
    Create a user with role provided
    """

    role, created = Group.objects.get_or_create(name=role)

    if enforce_new:
        created = False
        while not created:
            user = MyUser.objects.filter(email=f"{name}@myapp.com")

            if user.count() > 0:
                name = "".join([random.choice(string.ascii_letters) for x in range(8)])
            else:
                created = True

    user, created = MyUser.objects.get_or_create(
        role=role,
        phone="0723456780",
        verified=True,
        email=f"{name}@myapp.com",
        password="Pass1234",
        username=name,
        first_name=name,
        last_name="d.",
    )

    if created:
        user.set_password(user.password)
        user.save()

    return user


def create_default_admin():
    """
    Create admin user
    """
    return create_user(name="adminuser1", role="ADMIN")


def create_default_patient():
    """
    Create patient user
    """
    return create_user(name="p.user1", role="PATIENT")


def create_default_doctor():
    """
    Create doctor user
    """
    return create_user(name="d.user1", role="DOCTOR")


def create_default_users():
    """
    Create admin, patient and doc user
    """
    create_default_admin()
    create_default_patient()
    create_default_doctor()
