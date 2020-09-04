from rest_framework import permissions


class IsSelfOrAdminUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        is_self = obj == request.user
        is_admin = request.user.is_staff
        return is_self or is_admin
