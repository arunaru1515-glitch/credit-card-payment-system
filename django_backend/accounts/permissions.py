from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminUserRole(BasePermission):
    """
    Allows access only to Admin users (or Django superusers).
    """
    message = "Admin role permission required."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.role == "ADMIN" or request.user.is_superuser)
        )


class IsSupportUserRole(BasePermission):
    """
    Allows access to Support users and Admin users.
    """
    message = "Support or Admin role permission required."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.role in ["ADMIN", "SUPPORT"]
                or request.user.is_superuser
            )
        )


class IsReadOnlyUserRole(BasePermission):
    """
    Allows access to Read-Only, Support, and Admin users (staff/audit members).
    """
    message = "Read-Only, Support, or Admin role permission required."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.role in ["ADMIN", "SUPPORT", "READ_ONLY"]
                or request.user.is_superuser
            )
        )


class IsAdminOrReadOnlyRole(BasePermission):
    """
    Read access permitted for Read-Only, Support, and Admin.
    Write/mutation operations permitted only for Admin.
    """
    message = "Admin role required for write actions. Read-Only allowed for view."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        if request.method in SAFE_METHODS:
            return bool(
                request.user.role in ["ADMIN", "SUPPORT", "READ_ONLY"]
                or request.user.is_superuser
            )

        return bool(
            request.user.role == "ADMIN"
            or request.user.is_superuser
        )


class IsSupportOrAdminMutation(BasePermission):
    """
    Read access for Read-Only, Support, Admin.
    Support operations (e.g. card block/unblock) permitted for Support & Admin.
    """
    message = "Support or Admin role required."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        if request.method in SAFE_METHODS:
            return bool(
                request.user.role in ["ADMIN", "SUPPORT", "READ_ONLY"]
                or request.user.is_superuser
            )

        return bool(
            request.user.role in ["ADMIN", "SUPPORT"]
            or request.user.is_superuser
        )
