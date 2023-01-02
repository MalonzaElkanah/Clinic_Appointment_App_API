from rest_framework.permissions import BasePermission

from django.contrib.auth.models import Group


SAFE_METHODS = ['POST', 'HEAD', 'OPTIONS']

READ_SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']


class IsAuthenticatedOrPOSTOnly(BasePermission):
    """
    The request is authenticated as a user, or is a post-only request.
    """

    def has_permission(self, request, view):
        if (request.method in SAFE_METHODS or
                request.user and
                request.user.is_authenticated):
            return True
        return False


class IsOwnerOrReadOnly(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `user.id` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in READ_SAFE_METHODS:
            return True

        # Instance must have an attribute named `user.id`.
        return obj.user.id == request.user.id


class IsOwnerOrIsRoleAdmin(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it
     or a user with admin role.
    Assumes the model instance has an `user.id` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.user.role.name == "ADMIN":
            return True

        # Instance must have an attribute named `user.id`.
        return obj.user.id == request.user


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user.id == request.user.id


class IsRoleAdmin(BasePermission):
    """
    The request is authenticated as a user and has an Admin Role.
    """
    message = "Admin Only Access"

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.role is None:
            return False

        if request.user.role.name == "ADMIN":
            return True

        return request.user.is_staff


    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        if request.user.role is None:
            return False

        if request.user.role.name == "ADMIN":
            return True

        return request.user.is_staff


class IsRoleDoctor(BasePermission):
    """
    The request is authenticated as a user and has a Doctor Role.
    """
    message = "Doctor Only Access"

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.role.name == "DOCTOR":
            return True

        return False

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        if request.user.role.name == "DOCTOR":
            return True

        return False


class IsRolePatient(BasePermission):
    """
    The request is authenticated as a user and has a Patient Role.
    """
    message = "Patient Only Access"

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.role.name == "PATIENT":
            return True

        return False

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        if request.user.role.name == "PATIENT":
            return True

        return False

