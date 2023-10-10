from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django.http.response import StreamingHttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action

from .serializers import (
    TemplateSerializer,
    DocumentSerializer,
    DocumentFieldSerializer
)
from documents.models import (
    Document,
    DocumentField,
    Template,
    TemplateField
    )
from core.template_render import DocumentTemplate

class TemplateViewSet(viewsets.ModelViewSet):
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


class TemplateFieldViewSet(viewsets.ModelViewSet):
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


class DocumentViewSet(viewsets.ModelViewSet):
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

    @action(
        detail=True,
        permission_classes=[AllowAny, ],
        url_path=r'download_document'
    )
    def download_document(self, request, pk=None):

        document = get_object_or_404(Document, id=pk)
        context = dict()
        field = DocumentField.objects.filter(document_id=pk)
        serializers =  DocumentFieldSerializer(field, many=True)
        for field in serializers.data:
            name_field = TemplateField.objects.get(id=field['field_id'])
            context[str(name_field)] = field['value']

        path = document.template_id.template
        doc = DocumentTemplate(path)
        buffer = doc.get_draft(context)

        response = StreamingHttpResponse(
        streaming_content=buffer,  # use the stream's content
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        name = document.template_id.name
        response['Content-Disposition'] = f'attachment;filename={name}.docx'
        response["Content-Encoding"] = 'UTF-8'

        return response


class DocumentFieldViewSet(viewsets.ModelViewSet):
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
