from rest_framework import permissions
from users.models import UserRole

class IsAdmin(permissions.BasePermission):
    """
    Allows access only to Admin users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (
            request.user.role == UserRole.ADMIN or request.user.is_superuser
        ))

class IsManager(permissions.BasePermission):
    """
    Allows access to Manager users (and Admins).
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (
            request.user.role in [UserRole.MANAGER, UserRole.ADMIN] or request.user.is_superuser
        ))

class IsEmployee(permissions.BasePermission):
    """
    Allows access to Employee users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

class IsOwnerOrAdminOrManager(permissions.BasePermission):
    """
    Object-level permission to allow only owners of an object or Admins/Managers to edit it.
    Assumes the model instance has an `uploaded_by`, `created_by`, or `assigned_to` attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Admins and Managers have full permissions
        if request.user.is_superuser or request.user.role in [UserRole.ADMIN, UserRole.MANAGER]:
            return True
            
        # Check ownership
        owner_fields = ['created_by', 'uploaded_by', 'assigned_to', 'user']
        for field in owner_fields:
            if hasattr(obj, field):
                val = getattr(obj, field)
                if val == request.user:
                    return True
        return False
