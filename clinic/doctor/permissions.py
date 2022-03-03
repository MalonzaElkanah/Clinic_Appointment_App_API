from rest_framework.permissions import BasePermission


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
        queryset = view.get_queryset()
        if queryset.count() > 0:
            for obj in queryset:
                if obj.doctor.user.id == request.user.id:
                    return True 
        else:
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