from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers

from users.models import User


class SignUpUserSerializer(UserCreateSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'password'
        )
        read_only_fields = ('id',)


class CustomUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email'
        )
