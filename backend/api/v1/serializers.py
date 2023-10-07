from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers

User = get_user_model()

from documents.models import (
    Document,
    DocumentField,
    Template,
    TemplateField
    )


class TemplateSerializer(serializers.ModelSerializer):
    """ Заглушка. Сериализатор шаблонов. """
    class Meta:
        model = Template
        fields = '__all__'


class TemplateFieldSerializer(serializers.ModelSerializer):
    """ Заглушка. Сериализатор поля шаблона. """
    class Meta:
        model = TemplateField
        fields = '__all__'


class DocumentSerializer(serializers.ModelSerializer):
    """ Заглушка. Сериализатор документов. """
    class Meta:
        model = Document
        fields = '__all__'


class DocumentFieldSerializer(serializers.ModelSerializer):
    """ Заглушка. Сериализатор поля документов. """
    class Meta:
        model = DocumentField
        fields = '__all__'


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
