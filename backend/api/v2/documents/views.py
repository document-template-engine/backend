"""Вьюсеты v1 API."""
from datetime import datetime
import logging

from django.contrib.auth import get_user_model
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    filters,
    status,
    viewsets,
    views,
)
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from core.template_render import DocumentTemplate
from .serializers import (
    DocumentFieldSerializer,
    DocumentReadSerializerExtended,
    DocumentReadSerializerMinified,
    DocumentWriteSerializer,

)
from api.v2 import utils as v1utils
from documents.models import Document, Template

logger = logging.getLogger(__name__)

User = get_user_model()


def send_file(filestream, filename: str, as_attachment: bool = True):
    """Функция подготовки открытого двоичного файла к отправке."""
    response = FileResponse(
        streaming_content=filestream,
        as_attachment=as_attachment,
        filename=filename,
    )
    return response


class DocumentViewSet(viewsets.ModelViewSet):
    """Документ."""

    queryset = Document.objects.all()
    serializer_class = DocumentReadSerializerMinified
    http_method_names = ("get", "post", "patch", "delete")
    permission_classes = (IsAuthenticated,)
    # permission_classes = (AllowAny,) # Заглушка
    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    )
    pagination_class = None
    filterset_fields = ("owner",)
    search_fields = ("owner",)

    def get_queryset(self):
        """Выдаем только список документов текущего пользователя."""
        # ЗАглушка
        if self.request.user.is_authenticated:
            return self.request.user.documents
        else:
            user = User.objects.get(id=1)
            return Document.objects.filter(owner=user)
        return Document.objects.none()

    def get_serializer_class(self):
        """Выбор сериализатора."""
        if self.action == "retrieve":
            return DocumentReadSerializerExtended
        elif self.action == "list":
            return DocumentReadSerializerMinified
        return DocumentWriteSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(
        detail=False,
        permission_classes=[
            IsAuthenticated,
            # AllowAny,  # Заглушка
        ],
        url_path=r"draft",
    )
    def draft_documents(self, request):
        """Возвращает список незаконченных документов/черновиков"""
        user = self.request.user
        queryset = Document.objects.filter(completed=False, owner=user)
        serializer = DocumentReadSerializerMinified(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        permission_classes=[
            IsAuthenticated,
        ],
        url_path=r"history",
    )
    def history_documents(self, request):
        """Возвращает список законченных документов/история"""
        user = self.request.user
        queryset = Document.objects.filter(completed=True, owner=user)
        serializer = DocumentReadSerializerMinified(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        permission_classes=[
            IsAuthenticated
            ],
        url_path=r"download_document",
    )
    def download_document(self, request, pk=None):
        """Скачивание готового документа."""
        logger.debug(f"Start docx generation for document_id {pk}")
        start_time = datetime.utcnow()
        document = get_object_or_404(Document, id=pk)
        buffer = v1utils.fill_docx_template_for_document(document)
        docx_time = datetime.utcnow()
        logger.debug(
            f"Time of docx generation for document_id {pk} is {docx_time-start_time}"
        )
        response = send_file(buffer, f"{document.template.name}.docx")
        return response

    @action(
        detail=True,
        permission_classes=[
            IsAuthenticated
            ],
        url_path="download_pdf",
    )
    def download_pdf(self, request, pk=None):
        """Генерация и выдача на скачивание pdf-файла."""
        document = get_object_or_404(Document, pk=pk)
        logger.debug(f"Start docx generation for document_id {pk}")
        start_time = datetime.utcnow()
        buffer = v1utils.create_document_pdf_for_export(document)
        pdf_time = datetime.utcnow()
        logger.debug(
            f"Time of docx generation for document_id {pk} is {pdf_time-start_time}"
        )
        response = send_file(buffer, f"{document.template.name}.pdf")
        return response


class DocumentFieldViewSet(viewsets.ModelViewSet):
    """Поле шаблона."""

    queryset = Document.objects.all()
    serializer_class = DocumentFieldSerializer
    http_method_names = ("get",)
    permission_classes = (IsAuthenticated,)
    # permission_classes = (AllowAny,) # Заглушка
    pagination_class = None

    def get_queryset(self):
        document_id = self.kwargs.get("document_id")
        document = get_object_or_404(Document, id=document_id)
        if (
            not self.request.user.is_staff
            and document.owner != self.request.user
        ):
            raise PermissionDenied()
        return document.document_fields.all()


class AnonymousDownloadPreviewAPIView(views.APIView):
    permission_classes = (AllowAny,)

    def post(self, request, template_id):
        logger.debug(f"Start preview generation for template {template_id}")
        start_time = datetime.utcnow()
        template = get_object_or_404(Template, id=template_id)
        document_fields = request.data.get("document_fields")
        serializer = DocumentFieldWriteSerializer(
            data=document_fields,
            context={"template_fields": set(template.fields.all())},
            many=True,
        )
        serializer.is_valid(raise_exception=True)
        v1utils.custom_fieldtypes_validation(serializer.validated_data)
        context = {}
        for data in serializer.validated_data:
            if data["value"]:  # write only fields with non empty value
                context[data["field"].tag] = data["value"]
        context_default = {
            field.tag: field.default or field.name
            for field in template.fields.all()
        }
        doc = DocumentTemplate(template.template)
        buffer = doc.get_partial(context, context_default)
        filename = f"{template.name}_preview.docx"
        docx_time = datetime.utcnow()
        logger.debug(
            f"Time of docx generation for template {template_id} is {docx_time-start_time}"
        )
        if request.query_params.get("pdf"):
            buffer = v1utils.convert_file_to_pdf(buffer)
            filename = f"{template.name}_preview.pdf"
            pdf_time = datetime.utcnow()
            logger.debug(
                f"Time of pdf generation for template {template_id} is {pdf_time-docx_time}"
            )
        response = send_file(buffer, filename)
        return response

