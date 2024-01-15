"""Вьюсеты v1 API."""
import logging

from django.contrib.auth import get_user_model
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    filters,
    generics,
    serializers,
    status,
    views,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from api.v2.permissions import IsAdminOrReadOnly, IsOwner, IsOwnerOrAdminOrReadOnly
from .serializers import (
    TemplateFieldSerializer,
    TemplateFileUploadSerializer,
    TemplateSerializer,
    TemplateSerializerMinified,
    TemplateWriteSerializer,
)

from api.v2 import utils as v1utils
from core.constants import Messages
from core.template_render import DocumentTemplate
from documents.models import Template


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


class TemplateViewSet(viewsets.ModelViewSet):
    """Шаблон."""

    serializer_class = TemplateSerializer
    http_method_names = ("get", "delete", "post")
    permission_classes = (IsAdminOrReadOnly,)  # AllowAny
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    pagination_class = None
    filterset_fields = (
        "owner",
        "category",
    )
    search_fields = (
        "owner",
        "category",
    )

    def get_serializer_class(self):
        if self.action == "list":
            return TemplateSerializerMinified
        elif self.action == "create":
            return TemplateWriteSerializer
        return TemplateSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Template.objects.all()
        else:
            return Template.objects.filter(deleted=False)

    @action(
        detail=True,
        methods=["get"],
        permission_classes=(AllowAny,),
        url_path="download_draft",
        url_name="download_draft",
    )
    def download_draft(self, request, pk=None):
        # template = get_object_or_404(Template, pk=pk)
        template = serializers.PrimaryKeyRelatedField(
            many=False, queryset=Template.objects.all()
        ).to_internal_value(data=pk)
        context = {field.tag: field.name for field in template.fields.all()}
        path = template.template
        doc = DocumentTemplate(path)
        buffer = doc.get_draft(context)
        filename = f"{template.name}_шаблон.docx"
        if request.query_params.get("pdf"):
            buffer = v1utils.convert_file_to_pdf(buffer)
            filename = f"{template.name}_шаблон.pdf"
        response = send_file(buffer, filename)
        return response

    def destroy(self, request, *args, **kwargs):
        user = request.user
        template = self.get_object()
        if not (user == template.owner or user.is_superuser):
            return Response(status=status.HTTP_404_NOT_FOUND)
        if template.deleted:
            return Response(
                Messages.TEMPLATE_ALREADY_DELETED,
                status=status.HTTP_404_NOT_FOUND,
            )
        template.deleted = True
        template.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TemplateFieldViewSet(viewsets.ModelViewSet):
    """Поля шаблона."""

    serializer_class = TemplateFieldSerializer
    http_method_names = ("get",)
    permission_classes = (IsAdminOrReadOnly,)
        # permission_classes = (AllowAny,) # Заглушка
    pagination_class = None

    def get_queryset(self):
        template_id = self.kwargs.get("template_id")
        template = get_object_or_404(Template, id=template_id)
        return template.fields.all()


class CheckTemplateConsistencyAPIView(views.APIView):
    permission_classes = (IsAdminUser,)
    # permission_classes = (AllowAny,) # Заглушка

    def get(self, request, template_id):
        template = get_object_or_404(Template, id=template_id)
        errors = template.get_consistency_errors()
        if errors:
            return Response(data={"errors": errors}, status=status.HTTP_200_OK)
        else:
            return Response(
                data={"result": Messages.TEMPLATE_CONSISTENT},
                status=status.HTTP_200_OK,
            )


class UploadTemplateFileAPIView(generics.UpdateAPIView):
    queryset = Template.objects.all()
    serializer_class = TemplateFileUploadSerializer
    lookup_field = "id"
    lookup_url_kwarg = "template_id"
    permission_classes = (IsAdminUser,)
    # permission_classes = (AllowAny,) # Заглушка
    http_method_names = ["patch", "put"]
