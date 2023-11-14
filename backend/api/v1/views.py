"""Вьюсеты v1 API."""
import io
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List

import aspose.words as aw
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
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsAdminOrReadOnly, IsOwner, IsOwnerOrAdminOrReadOnly
from .serializers import (
    CategorySerializer,
    DocumentFieldForPreviewSerializer,
    DocumentFieldSerializer,
    DocumentReadSerializerExtended,
    DocumentReadSerializerMinified,
    DocumentWriteSerializer,
    FavDocumentSerializer,
    FavTemplateSerializer,
    TemplateFieldSerializer,
    TemplateFileUploadSerializer,
    TemplateSerializer,
    TemplateSerializerMinified,
    TemplateWriteSerializer,
)

# from api.v1.utils import Util
from core.constants import Messages
from core.template_render import DocumentTemplate
from documents.models import (
    Category,
    Document,
    FavDocument,
    FavTemplate,
    Template,
)

User = get_user_model()


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AllowAny,)


def send_file(filestream, filename: str, as_attachment: bool = True):
    """Функция подготовки открытого двоичного файла к отправке."""
    response = FileResponse(
        streaming_content=filestream,
        as_attachment=True,
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
        template = serializers.PrimaryKeyRelatedField(
            many=False, queryset=Template.objects.all()
        ).to_internal_value(data=pk)
        context = {field.tag: field.name for field in template.fields.all()}
        path = template.template
        doc = DocumentTemplate(path)
        buffer = doc.get_draft(context)
        filename = f"{template.name}_шаблон.docx"
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
    permission_classes = (AllowAny,)
    pagination_class = None

    def get_queryset(self):
        template_id = self.kwargs.get("template_id")
        template = get_object_or_404(Template, id=template_id)
        return template.fields.all()


class DocumentViewSet(viewsets.ModelViewSet):
    """Документ."""

    queryset = Document.objects.all()
    serializer_class = DocumentReadSerializerMinified
    http_method_names = ("get", "post", "patch", "delete")
    # permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)
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
            # IsAuthenticated,
            AllowAny,
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
        permission_classes=[IsAuthenticated],
        url_path=r"download_document",
    )
    def download_document(self, request, pk=None):
        """Скачивание готового документа."""
        document = get_object_or_404(Document, id=pk)
        context = dict()
        for docfield in document.document_fields.all():
            template_field = docfield.field
            context[template_field.tag] = docfield.value
        context_default = {
            field.tag: field.name for field in document.template.fields.all()
        }

        path = document.template.template
        doc = DocumentTemplate(path)
        buffer = doc.get_partial(context, context_default)
        response = send_file(buffer, f"{document.template.name}.docx")
        return response

    @action(
        detail=True,
        permission_classes=[IsAuthenticated],
        url_path="download_pdf",
    )
    def download_pdf(self, request, pk=None):
        """Генерация и выдача на скачивание pdf-файла."""
        with tempfile.NamedTemporaryFile() as output:
            outfile = Path(output.name).resolve()
            outfile.write_bytes(
                b"".join(self.download_document(request, pk).streaming_content)
            )
            subprocess.run(
                [
                    "soffice",
                    "--headless",
                    "--invisible",
                    "--nologo",
                    "--convert-to",
                    "pdf",
                    "--outdir",
                    outfile.parent,
                    outfile.absolute(),
                ]
            )
        newfile = outfile.with_suffix(".pdf")
        buffer = io.BytesIO(newfile.read_bytes())
        response = send_file(buffer, newfile.name)
        return response

    @action(
        detail=True,
        permission_classes=[IsOwner],
    )
    def download_pdf_aspose(self, request, pk=None):
        """Скачивание pdf-файла."""
        document = get_object_or_404(Document, id=pk, owner=request.user)
        docx_stream = io.BytesIO(
            b"".join(self.download_document(request, pk).streaming_content)
        )
        docx_file = aw.Document(docx_stream)
        buffer = io.BytesIO()
        docx_file.save(buffer, aw.SaveFormat.PDF)
        buffer.seek(0, os.SEEK_SET)
        response = send_file(buffer, f"{document.template.name}.pdf")
        return response


class DocumentFieldViewSet(viewsets.ModelViewSet):
    """Поле шаблона."""

    serializer_class = DocumentFieldSerializer
    http_method_names = ("get",)
    # permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)
    pagination_class = None

    def get_queryset(self):
        document_id = self.kwargs.get("document_id")
        document = get_object_or_404(Document, id=document_id)
        # ЗАглушка
        # if (
        #     not (self.request.user.is_authenticated)
        #     or document.owner != self.request.user
        # ):
        #     raise PermissionDenied()
        return document.document_fields.objects.all()


class FavTemplateAPIview(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, **kwargs):
        data = {
            "user": self.request.user.pk,
            "template": self.kwargs.get("template_id"),
        }
        serializer = FavTemplateSerializer(data=data)
        queryset = FavTemplate.objects.filter(
            user=self.request.user.pk, template=self.kwargs.get("template_id")
        )
        # проверка, что такого FavTemplate нет в БД
        if queryset.exists():
            raise serializers.ValidationError(
                "Этот шаблон уже есть в Избранном!"
            )
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        queryset = FavTemplate.objects.filter(
            user=self.request.user.pk, template=self.kwargs.get("template_id")
        )
        # проверка, что такой FavTemplate существует в БД
        if not queryset.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavDocumentAPIview(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, **kwargs):
        data = {
            "user": self.request.user.pk,
            "document": self.kwargs.get("document_id"),
        }
        serializer = FavDocumentSerializer(data=data)
        queryset = FavDocument.objects.filter(
            user=self.request.user.pk, document=self.kwargs.get("document_id")
        )
        # проверка, что такого FavDocument нет в БД
        if queryset.exists():
            raise serializers.ValidationError(
                "Этот документ уже есть в Избранном!"
            )
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        queryset = FavDocument.objects.filter(
            user=self.request.user.pk, document=self.kwargs.get("document_id")
        )
        # проверка, что такой FavDocument существует в БД
        if not queryset.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AnonymousDownloadPreviewAPIView(views.APIView):
    permission_classes = (AllowAny,)

    def post(self, request, template_id):
        template = get_object_or_404(Template, id=template_id)
        document_fields = request.data.get("document_fields")
        serializer = DocumentFieldForPreviewSerializer(
            data=document_fields,
            context={"template_fields": set(template.fields.all())},
            many=True,
        )
        serializer.is_valid(raise_exception=True)
        context = {}
        for data in serializer.validated_data:
            if data["value"]:  # write only fields with non empty value
                context[data["field"].tag] = data["value"]
        context_default = {
            field.tag: field.name for field in template.fields.all()
        }
        doc = DocumentTemplate(template.template)
        buffer = doc.get_partial(context, context_default)
        response = send_file(buffer, f"{template.name}_preview.docx")
        return response


class CheckTemplateConsistencyAPIView(views.APIView):
    permission_classes = (AllowAny,)  # isAdmin

    def get(self, request, template_id):
        template = get_object_or_404(Template, id=template_id)
        errors = template.get_consistency_errors()
        if errors:
            return Response(
                data={"result": Messages.TEMPLATE_CONSISTENT},
                status=status.HTTP_200_OK,
            )
        return Response(data={"errors": errors}, status=status.HTTP_200_OK)


class UploadTemplateFileAPIView(generics.UpdateAPIView):
    queryset = Template.objects.all()
    serializer_class = TemplateFileUploadSerializer
    lookup_field = "id"
    lookup_url_kwarg = "template_id"
    permission_classes = (IsAdminUser,)
    http_method_names = ["patch", "put"]

    # class UploadTemplateFileAPIView(views.APIView):
    #     serializer
    #     permission_classes = (AllowAny,)  # isAdmin

    #     def post(self, request, template_id):
    #         serializer = TemplateFileUploadSerializer(data=request.data)
    #         if serializer.is_valid():
    #             print(serializer.validated_data)
    #             # Process the uploaded file here
    #             # Save it to the server or perform any required operations
    #             return Response({"message": "File uploaded successfully"})
    #         else:
    #             return Response(
    #                 serializer.errors, status=status.HTTP_400_BAD_REQUEST
    #             )

    # template = get_object_or_404(Template, id=template_id)
    # excess_tags, excess_fields = template.get_inconsistent_tags()
    # if not excess_tags and not excess_fields:
    #     return Response(
    #         data={"result": Messages.TEMPLATE_CONSISTENT},
    #         status=status.HTTP_200_OK,
    #     )
    # context = {"errors": []}
    # if excess_tags:
    #     context["errors"].append(
    #         {"message": Messages.TEMPLATE_EXCESS_TAGS, "tags": excess_tags}
    #     )
    # if excess_fields:
    #     context["errors"].append(
    #         {
    #             "message": Messages.TEMPLATE_EXCESS_FIELDS,
    #             "tags": excess_fields,
    #         }
    #     )
    # return Response(data=context, status=status.HTTP_200_OK)


# class RegisterView(generics.GenericAPIView):
#     serializer_class = CustomUserSerializer

#     def post(self, request):
#         user = request.data
#         serializer = self.serializer_class(data=user)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         user_data = serializer.data
#         user = User.objects.get(email=user_data["email"])
#         token = RefreshToken.for_user(user).access_token

#         absurl = "https://documents-template.site/" + "?token=" + str(token)
#         email_body = (
#             "Hi "
#             + user.username
#             + " Use the link below to verify your email \n"
#             + absurl
#         )
#         data = {
#             "email_body": email_body,
#             "to_email": user.email,
#             "email_subject": "Verify your email",
#         }

#         Util.send_email(data)
#         return Response(user_data, status=status.HTTP_201_CREATED)
