from rest_framework.permissions import BasePermission

from clinic.models import Doctor


SAFE_METHODS = ['POST', 'HEAD', 'OPTIONS']

READ_SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']

ALL_SAFE_METHODS = ['POST', 'HEAD', 'OPTIONS', 'GET']

class ReadOnlyIfAuthenticatedOrPOSTOnly(BasePermission):

    message = "Read only Access if User is Authenticated or POST Only."

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.method in READ_SAFE_METHODS:
                return True
        elif request.method in SAFE_METHODS:
            return True
        return False


class IsOwnerDoctorOrReadOnly(BasePermission): 
    """
    Permission to only allow doctor-owner of an object to access it.
    Assumes the model instance has an `doctor.user.id` attribute.
    """
    message = "Edit or POST Access Only to the Doctor Owner or Read only."

    def has_permission(self, request, view):
        if request.user.role.name == "DOCTOR":
            doctor_id = view.kwargs.get('doctor_pk', 0)
            doctors = Doctor.objects.filter(user=request.user.id)
            if doctors.count() > 0:
                if doctors[0].id == int(doctor_id):
                    return True
            
        if request.method in READ_SAFE_METHODS:
            return True

        return False

    """
    Object-level permission to only allow doctor-owners of an object to edit it.
    Assumes the model instance has an `doctor.user.id` attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in READ_SAFE_METHODS:
            return True

        # Instance must have an attribute named `doctor.user.id`.
        return obj.doctor.user.id == request.user.id


class IsOwnerDoctorOrPatientPOSTOnly(BasePermission):
    """
    Owner or POST Only if Patient
    """

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.role.name == "PATIENT":
                if request.method in SAFE_METHODS:
                    return True
            elif request.user.role.name == "DOCTOR":
                doctor_id = view.kwargs.get('doctor_pk', 0)
                doctors = Doctor.objects.filter(user=request.user.id)
                if doctors.count() > 0:
                    if doctors[0].id == int(doctor_id):
                        return True

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            if request.method in SAFE_METHODS:
                # POST permissions are allowed to patients
                if request.user.role.name == "PATIENT":
                    return True
            elif obj.doctor.user.id == request.user.id:
                return True
        return False


class IsOwnerReviewOrDoctorReadOnly(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            # Doctor Read Safe Method
            if request.user.role.name == "DOCTOR":
                if request.method in READ_SAFE_METHODS:
                    return True
            elif request.user.role.name == "PATIENT":
                if request.method in ALL_SAFE_METHODS:
                    return True
                    
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            # Doctor Read Safe Method
            if request.user.role.name == "DOCTOR":
                if request.method in READ_SAFE_METHODS:
                    return True
            elif request.user.role.name == "PATIENT":
                if obj.appointment.patient.user.id == request.user.id:
                    return True
                elif request.method in ALL_SAFE_METHODS:
                    return True
            
        return False


