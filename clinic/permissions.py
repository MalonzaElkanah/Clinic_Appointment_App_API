from rest_framework.permissions import BasePermission


READ_SAFE_METHODS = ["GET", "HEAD", "OPTIONS"]


class IsOwnerOrReadOnly(BasePermission):

    message = "Read only Access."

    def has_object_permission(self, request, view, obj):
        if request.method in READ_SAFE_METHODS:
            return True

        return obj.user.id == request.user.id
