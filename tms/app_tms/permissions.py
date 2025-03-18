from rest_framework import permissions
from .models import Employees, Managers, Admins

class BaseRolePermission(permissions.BasePermission):
    """
    Base class for role-based permissions with method restrictions
    """
    allowed_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
    role_model = None  # Override in child classes

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        # Check if user has the required role
        if self.role_model and self.role_model.objects.filter(login_auth=request.user).exists():
            # Check allowed methods for this role
            return request.method in self.allowed_methods
        return False

    def has_object_permission(self, request, view, obj):
        # Default object permission (override in child classes if needed)
        return self.has_permission(request, view)
    
class IsEmployee(BaseRolePermission):
    """
    Employee permissions:
    - GET, POST, PUT/PATCH on own data
    - No DELETE access
    """
    allowed_methods = ['GET', 'POST', 'PUT', 'PATCH']
    role_model = Employees

    def has_permission(self, request, view):
        # print(f" Checking has_permission for IsEmployee: request.user={request.user}, request.method={request.method}")
        if not request.user.is_authenticated:
            # print(" User is not authenticated.")
            return False
        if Employees.objects.filter(login_auth=request.user).exists():
            # print(" User is an employee.")
            return request.method in self.allowed_methods
        # print(" User is not an employee.")
        return False

    def has_object_permission(self, request, view, obj):
        print(f" Checking has_object_permission for IsEmployee: request.user={request.user}, obj={obj}")
        if request.user.is_authenticated:
            if hasattr(obj, 'employee'):
                # print(f" Checking employee attribute: obj.employee.login_auth={obj.employee.login_auth}, request.user={request.user}")
                return obj.employee.login_auth == request.user
            elif hasattr(obj, 'requester'):  # For travel requests
                # print(f" Checking requester attribute: obj.requester.login_auth={obj.requester.login_auth}, request.user={request.user}")
                return obj.requester.login_auth == request.user
        # print(" User is not authenticated or object does not have required attributes.")
        return False


class IsManager(BaseRolePermission):
    """
    Manager permissions:
    - GET, PATCH on assigned requests
    """
    allowed_methods = ['GET', 'PATCH','POST','PUT']
    role_model = Managers

    def has_permission(self, request, view):
        # print(f" Checking has_permission for IsManager: user={request.user}, method={request.method}")
        if super().has_permission(request, view):
            return Managers.objects.filter(login_auth=request.user).exists()
        return False

    def has_object_permission(self, request, view, obj):
        # print(f" Checking has_object_permission for IsManager: user={request.user}, obj={obj}")

        user = request.user
        if hasattr(obj, 'assigned_manager'):
            return obj.assigned_manager.login_auth == user
        elif hasattr(obj, 'manager'):  # If object directly links to a manager
            return obj.manager.login_auth == user
        return False


class IsAdmin(BaseRolePermission):
    """
    Admin permissions:
    - Full access except user management
    - Superusers have unlimited access
    """
    allowed_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
    role_model = Admins

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
            
        # Admins can't modify other admins
        if isinstance(obj, Admins):
            return obj.login_auth == request.user
            
        # Admins have full access to non-admin objects
        return True

class IsOwner(permissions.BasePermission):
    """
    Generic ownership permission for any model with owner_field specification
    Usage: permission_classes = [IsOwner('user_field')]
    """
    def __init__(self, owner_field='user'):
        self.owner_field = owner_field

    def has_object_permission(self, request, view, obj):
        owner = getattr(obj, self.owner_field, None)
        return owner == request.user

#CombinedPermissions
IsEmployeeOrAdmin = IsEmployee | IsAdmin
IsManagerOrAdmin = IsManager | IsAdmin
IsOwnerOrAdmin = IsOwner() | IsAdmin
