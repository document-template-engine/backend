"""Сериализаторы для API."""
import base64
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files.base import ContentFile
from django.db import transaction
from djoser.serializers import UserSerializer
from rest_framework import serializers

from api.v2.utils import custom_fieldtypes_validation, get_non_unique_items
from core.constants import Messages
from documents.models import (
    Category,
    Document,
    DocumentField,
    FavDocument,
    FavTemplate,
    Template,
    TemplateField,
    TemplateFieldGroup,
    TemplateFieldType,
)

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


class TemplateFieldSerializer(serializers.ModelSerializer):
    """Сериализатор поля шаблона."""

    group_id = serializers.PrimaryKeyRelatedField(
        source="group", read_only=True
    )
    group_name = serializers.StringRelatedField(
        source="group.name", read_only=True
    )
    type = serializers.SlugRelatedField(slug_field="type", read_only=True)
    mask = serializers.CharField(source="type.mask", read_only=True)

    class Meta:
        model = TemplateField
        fields = (
            "id",
            "tag",
            "name",
            "hint",
            "group_id",
            "group_name",
            "type",
            "mask",
            "length",
        )


class TemplateFieldWriteSerializer(serializers.ModelSerializer):
    """Сериализатор поля шаблона для записи/обновления"""

    type = serializers.SlugRelatedField(
        queryset=TemplateFieldType.objects.all(), slug_field="type"
    )
    group = serializers.IntegerField(required=False, default=None)
    default = serializers.CharField(
        trim_whitespace=False, max_length=255, required=False
    )

    class Meta:
        model = TemplateField
        fields = ("tag", "name", "hint", "group", "type", "length", "default")


class TemplateFieldSerializerMinified(serializers.ModelSerializer):
    """Сериализатор поля шаблона сокращенный (без полей группы)"""

    type = serializers.SlugRelatedField(slug_field="type", read_only=True)
    mask = serializers.CharField(source="type.mask", read_only=True)

    class Meta:
        model = TemplateField
        fields = (
            "id",
            "tag",
            "name",
            "hint",
            "type",
            "mask",
            "length",
            "default",
        )


class TemplateGroupSerializerMinified(serializers.ModelSerializer):
    """Сериализатор группы полей шаблона без вложенных полей"""

    class Meta:
        model = TemplateFieldGroup
        fields = ("id", "name", )


class TemplateGroupSerializer(serializers.ModelSerializer):
    """Сериализатор группы полей шаблона"""

    fields = TemplateFieldSerializerMinified(
        read_only=True,
        many=True,
        # source="fields",
        allow_empty=True,
    )

    class Meta:
        model = TemplateField
        fields = (
            "id",
            "name",
            "fields",
        )

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["fields"].sort(key=lambda x: x["id"])
        return response


class TemplateGroupWriteSerializer(serializers.ModelSerializer):
    """Сериализатор группы полей шаблона для записи/обновления"""

    id = serializers.IntegerField()

    class Meta:
        model = TemplateFieldGroup
        fields = (
            "id",
            "name",
        )


class TemplateSerializerMinified(serializers.ModelSerializer):
    """Сериализатор шаблонов сокращенный."""

    is_favorited = serializers.SerializerMethodField()
    image = Base64ImageField(required=True, allow_null=True)

    class Meta:
        model = Template
        exclude = ("template",)
        read_only_fields = (
            "name",
            "category",
            "owner",
            "image",
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


class TemplateSerializerPlain(TemplateSerializerMinified):
    """Сериализатор шаблона (без вложенности полей в группы)."""

    fields = TemplateFieldSerializer(
        read_only=True,
        many=True,
        # source="fields",
        allow_empty=True,
    )

    groups = TemplateGroupSerializerMinified(
        source="field_groups",
        read_only=True,
        many=True,
        allow_empty=True,
    )

    class Meta(TemplateSerializerMinified.Meta):
        model = Template
        exclude = ("template",)
        # fields = "__all__"
        read_only_fields = ("is_favorited", "groups")


class TemplateSerializer(TemplateSerializerMinified):
    """Сериализатор шаблона (поля сгруппированы внутри grouped_fields)."""

    grouped_fields = TemplateGroupSerializer(
        read_only=True,
        many=True,
        source="field_groups",
        allow_empty=True,
    )
    ungrouped_fields = serializers.SerializerMethodField()

    class Meta(TemplateSerializerMinified.Meta):
        model = Template
        exclude = ("template",)
        read_only_fields = (
            "is_favorited",
            "grouped_fields",
            "ungrouped_fields",
        )

    def get_ungrouped_fields(self, instance):
        solo_fields = instance.fields.filter(group=None).order_by("id")
        return TemplateFieldSerializerMinified(solo_fields, many=True).data

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["grouped_fields"].sort(key=lambda x: x["id"])
        return response


class TemplateWriteSerializer(serializers.ModelSerializer):
    """Сериализатор шаблонов для записи/изменения."""

    fields = TemplateFieldWriteSerializer(many=True)
    groups = TemplateGroupWriteSerializer(many=True)

    class Meta:
        model = Template
        fields = ("name", "deleted", "description", "fields", "groups")

    def validate(self, data):
        # проверка, что все поля имеют уникальные тэги
        data_fields = data.get("fields")
        field_tags = [f["tag"] for f in data_fields]
        tags_duplicates = get_non_unique_items(field_tags)
        if tags_duplicates:
            raise serializers.ValidationError(
                detail=Messages.TEMPLATE_FIELD_TAGS_ARE_NOT_UNIQUE.format(
                    tags_duplicates
                )
            )

        # проверка, что все группы имеют уникальный id
        data_groups = data.get("groups")
        group_ids = [g["id"] for g in data_groups]
        ids_duplicates = get_non_unique_items(group_ids)
        if ids_duplicates:
            raise serializers.ValidationError(
                detail=Messages.TEMPLATE_GROUP_IDS_ARE_NOT_UNIQUE.format(
                    ids_duplicates
                )
            )

        # проверка, что поля шаблона привязаны к описанным группам в group
        field_groups = set([f.get("group") for f in data_fields])
        if None in field_groups:
            field_groups.discard(None)
        unknown_groups = field_groups - set(group_ids)
        if unknown_groups:
            raise serializers.ValidationError(
                detail=Messages.UNKNOWN_GROUP_ID.format(unknown_groups)
            )
        return data

    def create(self, data):
        data_fields = data.pop("fields")
        data_groups = data.pop("groups")
        template = Template.objects.create(**data)
        # создание групп
        data_groups.sort(key=lambda x: x["id"])
        group_models = {}
        for group in data_groups:
            model = TemplateFieldGroup.objects.create(
                name=group["name"], template=template
            )
            group_models[group["id"]] = model
        # создание полей
        template_fields = []
        for data in data_fields:
            group_id = data.get("group")
            if group_id:
                data["group"] = group_models[group_id]
            template_fields.append(TemplateField(template=template, **data))
        TemplateField.objects.bulk_create(template_fields)
        return template

    def to_representation(self, instance):
        request = self.context.get("request")
        return TemplateSerializerPlain(
            instance, context={"request": request}
        ).data


class TemplateFileUploadSerializer(serializers.ModelSerializer):
    errors = serializers.SerializerMethodField()

    class Meta:
        model = Template
        fields = ("template", "errors")

    def get_errors(self, instance):
        return instance.get_consistency_errors()
