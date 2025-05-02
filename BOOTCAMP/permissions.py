from rest_framework import permissions

class IsSuperUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_superuser

class IsSupportUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='support').exists()