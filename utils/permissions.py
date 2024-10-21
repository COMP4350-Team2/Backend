from rest_framework.permissions import BasePermission


class HasPermission(BasePermission):
    permission = None

    """
    User is allowed access if has the expected permission
    """
    def has_permission(self, request, view):
        """
        Checks user has the specified permissions
        """
        return request.auth and set(self.permission).issubset(request.auth.get('permissions', []))


class HasAdminPermission(HasPermission):
    permission = ['admin']


class HasMessagesPermission(HasPermission):
    permission = ['read:messages']
