from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from serializers import (
    TemplateSerializer,
    DocumentSerializer
)


class TemplateViewSet(viewsets):
    """ Заглушка. Шаблон. """
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    http_method_names = (
        'get',
        'post',
        'patch',
        'delete'
    )
    permissions_classes = (AllowAny,)


class TemplateFieldViewSet(viewsets):
    """ Заглушка. Поле шаблона. """
    queryset = TemplateField.objects.all()
    serializer_class = TemplateSerializer
    http_method_names = (
        'get',
        'post',
        'patch',
        'delete'
    )
    permissions_classes = (AllowAny,)


class DocumentViewSet(viewsets):
    """ Заглушка. Документ. """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    http_method_names = (
        'get',
        'post',
        'patch',
        'delete'
    )
    permissions_classes = (AllowAny,)


class DocumentFieldViewSet(viewsets):
    """ Заглушка. Поле документа. """
    queryset = DocumentField.objects.all()
    serializer_class = DocumentSerializer
    http_method_names = (
        'get',
        'post',
        'patch',
        'delete'
    )
    permissions_classes = (AllowAny,)
