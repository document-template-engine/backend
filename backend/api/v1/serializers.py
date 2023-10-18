from typing import Dict, List

from django.contrib.auth import get_user_model
from django.db import transaction
from djoser.serializers import UserSerializer
from rest_framework import serializers

from documents.models import (
    Category,
    Document,
    DocumentField,
    FavDocument,
    FavTemplate,
    FieldToDocument,
    Template,
    TemplateField,
)

User = get_user_model()


class TemplateFieldSerializer(serializers.ModelSerializer):
    """Сериализатор поля шаблона."""

    group_id = serializers.PrimaryKeyRelatedField(
        source="group", read_only=True
    )
    group_name = serializers.StringRelatedField(
        source="group.name", read_only=True
    )

    class Meta:
        model = TemplateField
        fields = ("id", "tag", "name", "hint", "group_id", "group_name")


class TemplateSerializerMinified(serializers.ModelSerializer):
    """Сериализатор шаблонов сокращенный."""

    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Template
        exclude = ("template",)
        read_only_fields = (
            "name",
            "category",
            "owner",
            "modified",
            "deleted",
            "description",
            "is_favorited",
        )

    def get_is_favorited(self, template: Template) -> bool:
        user = self.context.get("request").user
        if not user.is_authenticated:
            return False
        return FavTemplate.objects.filter(
            user=user, template=template
        ).exists()


class TemplateSerializer(TemplateSerializerMinified):
    """Сериализатор шаблона."""

    fields = TemplateFieldSerializer(
        read_only=True,
        many=True,
        # source="fields",
        allow_empty=True,
    )

    class Meta(TemplateSerializerMinified.Meta):
        model = Template
        exclude = ("template",)
        # fields = "__all__"
        read_only_fields = ("is_favorited",)


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


class DocumentFieldSerializer(serializers.ModelSerializer):
    """Сериализатор поля документов."""

    description = serializers.CharField(required=False, max_length=200)

    class Meta:
        model = DocumentField
        fields = "__all__"


class DocumentReadSerializer(serializers.ModelSerializer):
    """Сериализатор документов."""

    document_fields = DocumentFieldSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = (
            "id",
            "created",
            "updated",
            "completed",
            "description",
            "template",
            "owner",
            "document_fields",
            "is_favorited",
        )

    def get_is_favorited(self, document: Document) -> bool:
        user = self.context.get("request").user
        if not user.is_authenticated:
            return False
        return FavDocument.objects.filter(
            user=user, document=document
        ).exists()


class DocumentWriteSerializer(serializers.ModelSerializer):
    """Сериализатор документов."""

    document_fields = DocumentFieldSerializer(many=True)

    class Meta:
        model = Document
        fields = (
            "id",
            "created",
            "completed",
            "description",
            "template",
            "document_fields",
        )

    @transaction.atomic
    def create(self, validated_data):
        """Пока говно код. Создание документа и полей документа"""
        document_fields = validated_data.pop("document_fields")
        document = Document.objects.create(**validated_data)
        for data in document_fields:
            field = data["field"]
            template = TemplateField.objects.get(id=field.id).template
            if (
                document.template == template
            ):  # Эту проверку надо в валидатор засунуть. Проверяется, принадлежит ли поле выбраному шаблону
                field = DocumentField.objects.create(
                    field=field, value=data["value"]
                )
                FieldToDocument.objects.create(fields=field, document=document)
        return document

    @transaction.atomic
    def update(self, instance, validated_data):
        """Пока говно код. Обновление документа и полей документа"""
        document_fields = validated_data.pop("document_fields")
        Document.objects.filter(id=instance.id).update(**validated_data)
        document = Document.objects.get(id=instance.id)
        FieldToDocument.objects.filter(document=document).delete()
        for data in document_fields:
            field = data["field"]
            template = TemplateField.objects.get(id=field.id).template
            if (
                document.template == template
            ):  # Эту проверку надо в валидатор засунуть. Проверяется, принадлежит ли поле выбраному шаблону
                field = DocumentField.objects.create(
                    field=data["field"], value=data["value"]
                )
                FieldToDocument.objects.create(fields=field, document=document)
        return instance


class FavTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavTemplate
        fields = "__all__"


class FavDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavDocument
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
