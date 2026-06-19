from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminAndIsAuthenticatedOrReadOnly(BasePermission):

    def has_permission(self, request, view) -> bool:
        return bool(
            (request.user and request.method in SAFE_METHODS)
            or (
                request.user and request.user.is_authenticated
                and request.user.is_staff
            )
        )
