from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers

from documents.models import Document, DocumentField, Template, TemplateField

User = get_user_model()


class TemplateFieldSerializer(serializers.ModelSerializer):
    """Сериализатор поля шаблона."""

    class Meta:
        model = TemplateField
        fields = ("id", "tag", "name", "hint")


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
        #  TODO: return Favorite.filter(user=user, template=template).exists()
        return True


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


class DocumentSerializer(serializers.ModelSerializer):
    """Заглушка. Сериализатор документов."""

    class Meta:
        model = Document
        fields = "__all__"


class DocumentFieldSerializer(serializers.ModelSerializer):
    """Заглушка. Сериализатор поля документов."""

    class Meta:
        model = DocumentField
        fields = "__all__"


class CustomUserSerializer(UserSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "password")
        read_only_fields = ("id",)

    def create(self, validated_data):
        email = validated_data.get("email")
        password = validated_data.get("password")
        user = User(email=email)
        user.set_password(password)
        user.save()
        return user
