"""Reusable role-based permission classes."""

from rest_framework.permissions import SAFE_METHODS, BasePermission


class RoleMixin:
    """Helpers to inspect the authenticated user's role."""

    @staticmethod
    def _role(request):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return None
        return getattr(user, "role", None)


class IsSuperAdmin(RoleMixin, BasePermission):
    message = "Super admin access required."

    def has_permission(self, request, view):
        from apps.accounts.enums import UserRole

        return self._role(request) == UserRole.SUPER_ADMIN


class IsWorkshopOwner(RoleMixin, BasePermission):
    message = "Workshop owner access required."

    def has_permission(self, request, view):
        from apps.accounts.enums import UserRole

        return self._role(request) in {UserRole.WORKSHOP_OWNER, UserRole.SUPER_ADMIN}


class IsCustomer(RoleMixin, BasePermission):
    message = "Customer access required."

    def has_permission(self, request, view):
        from apps.accounts.enums import UserRole

        return self._role(request) in {UserRole.CUSTOMER, UserRole.SUPER_ADMIN}


class ReadOnlyOrSuperAdmin(RoleMixin, BasePermission):
    """Anyone can read; only super admins can write. Used for the catalog."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        from apps.accounts.enums import UserRole

        return self._role(request) == UserRole.SUPER_ADMIN
