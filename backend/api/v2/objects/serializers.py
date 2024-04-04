"""Сериализаторы для API."""
from rest_framework import serializers

from base_objects.models import (
    BaseObject,
    Object,
    BaseObjectField,
    ObjectField,
    )


class BaseObjectSerializer(serializers.ModelSerializer):
    """Сериализатор поля документов."""

    class Meta:
        fields = '__all__'
        model = BaseObject


class BaseObjectFieldSerializer(serializers.ModelSerializer):
    """Сериализатор поля документов."""

    class Meta:
        fields = '__all__'
        model = BaseObjectField


class ObjectSerializer(serializers.ModelSerializer):
    """Сериализатор поля документов."""

    class Meta:
        fields = '__all__'
        model = Object


class ObjectFieldSerializer(serializers.ModelSerializer):
    """Сериализатор поля документов."""

    class Meta:
        fields = '__all__'
        model = ObjectField