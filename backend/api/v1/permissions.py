"""Разрешения для API."""

from rest_framework import permissions


class IsSuperUserOrReadOnly(permissions.BasePermission):
    """Доступ: Администратор или только просмотр."""

    def has_permission(self, request, view):
        """Выдача прав на уровне списка."""
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_superuser
        )


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """Доступ: Владелец/админ или только для чтения"""

    def has_permission(self, request, view):
        """Видеть список могут все, добавлять только авторизованные."""
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """Под объектом подразумевается Template или Document."""
        return obj.owner == request.user or request.user.is_superuser
