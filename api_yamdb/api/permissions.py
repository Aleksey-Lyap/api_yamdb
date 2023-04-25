from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Доступ на чтения и изменения только админам."""

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated
                    and (request.user.role == 'admin'
                         or request.user.is_superuser)))


class IsAdmin(permissions.BasePermission):
    """Доступ только администратору."""

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and (request.user.role == 'admin'
                     or request.user.is_superuser))


class IsAuthorOrAdministratorOrReadOnly(permissions.BasePermission):
    """Изменения для админов и авторов, для остальных чтение."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            and request.user.is_anonymous
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.role == 'admin'
            or request.user.is_superuser
            or request.user.role == 'moderator'
        )
