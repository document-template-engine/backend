from django.http import FileResponse
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django.http.response import StreamingHttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action

from .serializers import (
    TemplateFieldSerializer,
    TemplateSerializer,
    TemplateSerializerMinified,
    DocumentSerializer,
    DocumentFieldSerializer,
)
from documents.models import Document, DocumentField, Template, TemplateField
from core.template_render import DocumentTemplate


def send_file(filestream, filename: str):
    """Функция подготовки открытого двоичного файла к отправке."""

    response = FileResponse(
        streaming_content=filestream,
        as_attachment=True,
        filename=filename,
    )
    return response


class TemplateViewSet(viewsets.ModelViewSet):
    """Шаблон."""

    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    http_method_names = ("get",)
    permissions_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action == "list":
            return TemplateSerializerMinified
        return TemplateSerializer

    @action(
        detail=True,
        permission_classes=[
            AllowAny,
        ],
        url_path=r"download_draft",
    )
    def download_draft(self, request, pk=None):
        template = get_object_or_404(Template, id=pk)
        context = {field.tag: field.name for field in template.fields.all()}
        path = template.template
        doc = DocumentTemplate(path)
        buffer = doc.get_draft(context)
        filename = f"{template.name}_шаблон.docx"
        response = send_file(buffer, filename)
        return response


class TemplateFieldViewSet(viewsets.ModelViewSet):
    """Поля шаблона."""

    serializer_class = TemplateFieldSerializer
    http_method_names = ("get",)
    permissions_classes = (AllowAny,)

    def get_queryset(self):
        template_id = self.kwargs.get("template_id")
        template = get_object_or_404(Template, id=template_id)
        return template.fields.all()


class DocumentViewSet(viewsets.ModelViewSet):
    """Заглушка. Документ."""

    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    http_method_names = ("get", "post", "patch", "delete")
    permissions_classes = (AllowAny,)

    @action(
        detail=True,
        permission_classes=[
            AllowAny,
        ],
        url_path=r"download_document",
    )
    def download_document(self, request, pk=None):
        document = get_object_or_404(Document, id=pk)
        context = dict()
        field = DocumentField.objects.filter(document_id=pk)
        serializers = DocumentFieldSerializer(field, many=True)
        for field in serializers.data:
            name_field = TemplateField.objects.get(id=field["field_id"])
            context[str(name_field)] = field["value"]

        path = document.template_id.template
        doc = DocumentTemplate(path)
        buffer = doc.get_draft(context)

        response = StreamingHttpResponse(
            streaming_content=buffer,  # use the stream's content
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        name = document.template_id.name
        response["Content-Disposition"] = f"attachment;filename={name}.docx"
        response["Content-Encoding"] = "UTF-8"

        return response


class DocumentFieldViewSet(viewsets.ModelViewSet):
    """Заглушка. Поле документа."""

    queryset = DocumentField.objects.all()
    serializer_class = DocumentSerializer
    http_method_names = ("get", "post", "patch", "delete")
    permissions_classes = (AllowAny,)
