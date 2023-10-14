from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers
from django.db import transaction

User = get_user_model()

from documents.models import (
    Document,
    DocumentField,
    Template,
    TemplateField,
    Documents
    FieldToDocument
    FavTemplate,
    FavDocument,
    Category,
)



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


class DocumentFieldSerializer(serializers.ModelSerializer):
    """ Сериализатор поля документов. """
    class Meta:
        model = DocumentField
        fields = '__all__'


class DocumentReadSerializer(serializers.ModelSerializer):
    """ Сериализатор документов. """
    document_fields = DocumentFieldSerializer(many=True)
    class Meta:
        model = Document
        fields = (
            'id',
            'created',
            'completed',
            "description",
            'template',
            'owner',
            'document_fields'
        )


class DocumentWriteSerializer(serializers.ModelSerializer):
    """ Сериализатор документов. """
    document_fields = DocumentFieldSerializer(many=True)
    class Meta:
        model = Document
        fields = (
            'id',
            'created',
            'completed',
            "description",
            'template',
            'document_fields'
        )
    
    @transaction.atomic
    def create(self, validated_data):
        """ Пока говно код. Создание документа и полей документа """
        document_fields = validated_data.pop("document_fields")
        document = Document.objects.create(**validated_data)
        for data in document_fields:
            field = data['field']
            template = TemplateField.objects.get(id=field.id).template_id
            if document.template == template: # Эту проверку надо в валидатор засунуть. Проверяется, принадлежит ли поле выбраному шаблону
                field = DocumentField.objects.create(field=field, value=data['value'])
                FieldToDocument.objects.create(fields=field, document=document)            
        return document

    @transaction.atomic
    def update(self, instance, validated_data):
        """ Пока говно код. Обновление документа и полей документа """
        document_fields = validated_data.pop("document_fields")
        Document.objects.filter(id=instance.id).update(**validated_data)
        document = Document.objects.get(id=instance.id)
        FieldToDocument.objects.filter(document=document).delete()
        for data in document_fields:
            field = data['field']
            template = TemplateField.objects.get(id=field.id).template
            if document.template == template: # Эту проверку надо в валидатор засунуть. Проверяется, принадлежит ли поле выбраному шаблону
                field = DocumentField.objects.create(field=data['field'], value=data['value'])
                FieldToDocument.objects.create(fields=field, document=document) 
        return instance


class FavTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = FavTemplate
        fields = '__all__'


class FavDocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = FavDocument
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = '__all__'

