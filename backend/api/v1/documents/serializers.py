"""Сериализаторы для API."""
import base64
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import serializers

from api.v1.utils import custom_fieldtypes_validation
from api.v1.templates.serializers import (TemplateGroupSerializer,
                                          TemplateSerializerMinified,
                                          TemplateFieldSerializerMinified)
from core.constants import Messages
from documents.models import (
    Document,
    DocumentField,)

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


class DocumentFieldSerializer(serializers.ModelSerializer):
    """Сериализатор поля документов."""

    description = serializers.CharField(required=False, max_length=200)

    class Meta:
        model = DocumentField
        exclude = ("document",)


class DocumentFieldWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для полей документа или превью шаблона."""

    # description = serializers.CharField(required=False, max_length=200)

    class Meta:
        model = DocumentField
        fields = ("field", "value")

    def validate_field(self, template_field):
        template_fields = self.context.get("template_fields", set())
        if template_field not in template_fields:
            raise serializers.ValidationError(
                Messages.WRONG_TEMPLATE_FIELD.format(template_field.id)
            )
        return template_field


class DocumentReadSerializerMinified(serializers.ModelSerializer):
    """Сериализатор документов сокращенный (без информации о полях)"""

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
            "is_favorited",
        )

    def get_is_favorited(self, document: Document) -> bool:
        user = self.context.get("request").user
        if not user.is_authenticated:
            return False
        return FavDocument.objects.filter(
            user=user, document=document
        ).exists()


class DocumentReadSerializerExtended(serializers.ModelSerializer):
    """Сериализатор документов расширенный (с информацией полей шаблона)."""

    grouped_fields = TemplateGroupSerializer(
        read_only=True,
        many=True,
        source="template.field_groups",
        allow_empty=True,
    )
    ungrouped_fields = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    template = TemplateSerializerMinified(read_only=True)

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
            "is_favorited",
            "grouped_fields",
            "ungrouped_fields",
        )

    def get_is_favorited(self, document: Document) -> bool:
        user = self.context.get("request").user
        if not user.is_authenticated:
            return False
        return FavDocument.objects.filter(
            user=user, document=document
        ).exists()

    def get_ungrouped_fields(self, instance):
        solo_fields = instance.template.fields.filter(group=None).order_by(
            "id"
        )
        return TemplateFieldSerializerMinified(solo_fields, many=True).data

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["grouped_fields"].sort(key=lambda x: x["id"])
        # add field values
        field_vals = {}
        for document_field in instance.document_fields.all():
            field_vals[document_field.field.id] = document_field.value
        for group in response["grouped_fields"]:
            for field in group["fields"]:
                id = field.get("id")
                if id in field_vals:
                    field["value"] = field_vals[id]
        for field in response["ungrouped_fields"]:
            id = field.get("id")
            if id in field_vals:
                field["value"] = field_vals[id]
        return response


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
        """Создание документа и полей документа"""
        document_fields = validated_data.pop("document_fields", None)
        document = Document.objects.create(**validated_data)
        custom_fieldtypes_validation(document_fields)
        document.create_document_fields(document_fields)
        return document

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновление документа и полей документа"""
        document_fields = validated_data.pop("document_fields", None)
        Document.objects.filter(id=instance.id).update(
            **validated_data, updated=timezone.now()
        )
        document = Document.objects.get(id=instance.id)
        if document_fields is not None:
            custom_fieldtypes_validation(document_fields)
            document.document_fields.all().delete()
            document.create_document_fields(document_fields)
        return document

    def to_representation(self, instance):
        return DocumentReadSerializerMinified(
            instance, context={"request": self.context.get("request")}
        ).data
