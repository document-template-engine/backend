from rest_framework import serializers


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