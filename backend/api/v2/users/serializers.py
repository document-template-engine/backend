"""Сериализаторы для API."""

from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers


User = get_user_model()


class CustomUserSerializer(UserSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "password")
        read_only_fields = ("id",)

    def create(self, validated_data):
        email = validated_data.get("email")
        password = validated_data.get("password")
        username = email
        user = User(email=email, username=username)
        user.set_password(password)
        user.save()
        return user

    def validate(self, data):
        if User.objects.filter(email=data["email"]):
            raise serializers.ValidationError("Такой email уже есть!")
        return data
