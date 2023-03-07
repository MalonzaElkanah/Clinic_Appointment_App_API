from rest_framework.permissions import BasePermission


READ_SAFE_METHODS = ["GET", "HEAD", "OPTIONS"]


class IsRoleAdminOrReadOnly(BasePermission):
    """
    The request is authenticated as a user and has an Admin Role,
    or is a read only request.
    """

    message = "Admin only Access."

    def has_permission(self, request, view):
        if request.method in READ_SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False

        if request.user.role is None:
            return False

        return request.user.role.name == "ADMIN"

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        if request.user.role is None:
            return False

        if request.user.role.name == "ADMIN":
            return True

        if request.method in READ_SAFE_METHODS:
            return True

        return request.user.is_staff
