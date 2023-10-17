from rest_framework import permissions


class IsSuperUserOrReadOnly(permissions.BasePermission):
    """ Доступ: Администратор или только просмотр"""
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_superuser)


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """ Доступ: Владелец/админ """
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """ Под объектом подразумевается Template или Document"""
        return (obj.owner == request.user
                or obj.owner == request.user.is_superuser)


class IsAuthenticated(permissions.BasePermission):
    """ Доступ: только авторизированный пользователь """
    def has_permission(self, request, view):
        return request.user.is_authenticated
