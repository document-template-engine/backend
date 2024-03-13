"""Сериализаторы для API."""
from django.contrib.auth import get_user_model
from rest_framework import serializers

from documents.models import (
    FavDocument,
    FavTemplate,
)

User = get_user_model()


class FavTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavTemplate
        fields = "__all__"


class FavDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavDocument
        fields = "__all__"
