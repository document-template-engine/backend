from djoser.serializers import UserSerializer
from rest_framework import serializers

from users.models import User


class CustomUserSerializer(UserSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'password'
        )
        read_only_fields = ('id',)

    def create(self, validated_data):
        email = validated_data.get('email')
        password = validated_data.get('password')
        user = User(email=email)
        user.set_password(password)
        user.save()
        return user
