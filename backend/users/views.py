from djoser.views import UserViewSet
from rest_framework import permissions

from users.models import User
from users.serializers import SignUpUserSerializer, CustomUserSerializer


class CustomUserViewSet(UserViewSet):
    """
    Регистрация, и аутентификация пользователей.
    """
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    http_method_names = ('get', 'post')
    permission_classes_by_action = {
        'create': [permissions.AllowAny],
        'list': [permissions.IsAdminUser],
    }

    def get_serializer_class(self):
        if self.action == 'create':
            return SignUpUserSerializer
        return CustomUserSerializer
