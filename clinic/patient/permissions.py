from rest_framework.permissions import BasePermission

from django.contrib.auth.models import Group


SAFE_METHODS = ['POST', 'HEAD', 'OPTIONS']

READ_SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']

ALL_SAFE_METHODS = ['POST', 'HEAD', 'OPTIONS', 'GET']


class IsOwnerDoctorOrReadOnly(BasePermission): 
    """
    Object-level permission to only allow doctor-owners of an object to edit it.
    Assumes the model instance has an `doctor.user.id` attribute.
    """
    message = "Access Only to the Doctor who created it."

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD, POST or OPTIONS requests.
        if request.method in ALL_SAFE_METHODS:
            return True

        # Instance must have an attribute named `doctor.user.id`.
        return obj.doctor.user.id == request.user.id


class IsDoctorOrReadOnly(BasePermission):
    """
    The request is authenticated as a Doctor, or is a read only request.
    """
    message = "Doctor only Access."

    def has_permission(self, request, view):
        if request.method in READ_SAFE_METHODS:
            return True
        return request.user.role.name == "DOCTOR"


class IsOwnerOrDoctor(BasePermission):
    """
    The request is authenticated as a Doctor or Owner.
    """
    message = "Only a Doctor or the Owner can Access."

    def has_permission(self, request, view):
        if request.user.role.name == "DOCTOR":
            return True
        queryset = view.get_queryset()
        if queryset.count() > 0:
            for obj in queryset:
                if obj.patient.user.id == request.user.id:
                    return True 
        else:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.role.name == "DOCTOR":
            return True
        return obj.patient.user.id == request.user.id


class IsOwnerDoctorOrIsOwnerPatient(BasePermission): 
    """
    Permission to only allow doctor-owners/patient-owners of an object to access it.
    Assumes the model instance has an `doctor.user.id` or `patient.user.id` attribute.
    """
    message = "Access Only to the Doctor or Patient referred."

    def has_permission(self, request, view):
        queryset = view.get_queryset()
        if queryset.count() > 0:
            for obj in queryset:
                if obj.patient.user.id == request.user.id:
                    return True 
                elif obj.doctor.user.id == request.user.id:
                    return True 
        else:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        if obj.doctor.user.id == request.user.id:
            return True
        elif obj.patient.user.id == request.user.id:
            return True

        return False


class IsOwnerPatient(BasePermission): 
    """
    Permission to only allow patient-owners of an object or queryset to access it.
    Assumes the model instance has an `patient.user.id` attribute.
    """
    message = "Access Only Patient Owner."

    def has_permission(self, request, view):
        queryset = view.get_queryset()
        if queryset.count() > 0:
            for obj in queryset:
                if obj.patient.user.id == request.user.id:
                    return True 
        else:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        return obj.patient.user.id == request.user.id

class IsOwnerOrDoctorReadOnly(BasePermission):

    message = "Only owner Access or Doctor Read only Access."

    def has_object_permission(self, request, view, obj):
        if request.method in READ_SAFE_METHODS:
            if request.user.role.name == "DOCTOR":
                return True
        return obj.user.id == request.user.id


class DoctorReadOnlyIfAuthenticatedOrPOSTOnly(BasePermission):

    message = "Doctor Read only Access if User is Authenticated or POST Only."

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.method in READ_SAFE_METHODS:
                if request.user.role.name == "DOCTOR":
                    return True
            return False
        elif request.method in SAFE_METHODS:
            return True
        return False
