from io import BytesIO
import subprocess
import tempfile
from pathlib import Path

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, serializers, status, views, viewsets, generics
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

from rest_framework_simplejwt.tokens import RefreshToken
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

from .utils import Util
from .permissions import IsOwnerOrAdminOrReadOnly
from .serializers import (
    CustomUserSerializer,
    CategorySerializer,
    DocumentFieldForPreviewSerializer,
    DocumentFieldSerializer,
    DocumentReadSerializer,
    DocumentWriteSerializer,
    FavDocumentSerializer,
    FavTemplateSerializer,
    TemplateFieldSerializer,
    TemplateSerializer,
    TemplateSerializerMinified,
)
from core.constants import Messages
from core.template_render import DocumentTemplate
from documents.models import (
    Category,
    Document,
    DocumentField,
    FavDocument,
    FavTemplate,
    FieldToDocument,
    Template,
)

User = get_user_model()

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permissions_classes = (AllowAny,)


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
    http_method_names = ("get", "delete")
    permissions_classes = (AllowAny,)
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
        return TemplateSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Template.objects.all()
        else:
            return Template.objects.filter(deleted=False)

    @action(
        detail=True,
        permission_classes=(AllowAny,),
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
    permissions_classes = (AllowAny,)
    pagination_class = None

    def get_queryset(self):
        template_id = self.kwargs.get("template_id")
        template = get_object_or_404(Template, id=template_id)
        return template.fields.all()


class DocumentViewSet(viewsets.ModelViewSet):
    """Документ."""

    queryset = Document.objects.all()
    serializer_class = DocumentReadSerializer
    http_method_names = ("get", "post", "patch", "delete")
    permissions_classes = (IsAuthenticated,)
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
        if self.request.user.is_authenticated:
            return self.request.user.documents
        return Document.objects.none()

    def get_serializer_class(self):
        """Выбор сериализатора."""
        if self.action in ["list", "retrieve"]:
            return DocumentReadSerializer
        return DocumentWriteSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(
        detail=False,
        permission_classes=[
            IsAuthenticated,
        ],
        url_path=r"draft",
    )
    def draft_documents(self, request):
        """Возвращает список незаконченных документов/черновиков"""
        user = self.request.user
        queryset = Document.objects.filter(completed=False, owner=user)
        serializer = DocumentReadSerializer(
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
        serializer = DocumentReadSerializer(
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
        for docfield in FieldToDocument.objects.filter(document=document):
            template_field = docfield.fields.field
            context[template_field.tag] = docfield.fields.value
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
        permissions_classes=[IsAuthenticated],
        url_path="download_pdf",
    )
    def download_pdf(self, request, pk=None):
        """Генерация и выдача на скачивание pdf-файла."""
        with tempfile.NamedTemporaryFile() as output:
            outfile = Path(output.name).resolve()
            outfile.write_bytes(
                b''.join(self.download_document(request, pk).streaming_content)
            )
            subprocess.run([
                "soffice",
                 "--headless",
                 "--invisible",
                 "--nologo",
                 "--convert-to",
                 "pdf",
                 "--outdir",
                 outfile.parent,
                 outfile.absolute(),
            ])
        newfile = outfile.with_suffix(".pdf")
        buffer = BytesIO(newfile.read_bytes())
        response = send_file(buffer, newfile.name)
        return response
            

class DocumentFieldViewSet(viewsets.ModelViewSet):
    """Поле шаблона."""

    serializer_class = DocumentFieldSerializer
    http_method_names = ("get",)
    permissions_classes = (IsAuthenticated,)
    pagination_class = None

    def get_queryset(self):
        document_id = self.kwargs.get("document_id")
        document = get_object_or_404(Document, id=document_id)
        if (
            not (self.request.user.is_authenticated)
            or document.owner != self.request.user
        ):
            raise PermissionDenied()
        through_set = FieldToDocument.objects.filter(document=document).all()
        return DocumentField.objects.filter(fieldtodocument__in=through_set)


class FavTemplateAPIview(APIView):
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
            raise serializers.ValidationError(
                "Этот шаблон отсутствует в Избранном!"
            )
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavDocumentAPIview(APIView):
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
            raise serializers.ValidationError(
                "Этот документ отсутствует в Избранном!"
            )
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



class RegisterView(generics.GenericAPIView):

    serializer_class = CustomUserSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = User.objects.get(email=user_data['email'])
        token = RefreshToken.for_user(user).access_token

        absurl = 'https://documents-template.site/'+"?token="+str(token)
        email_body = 'Hi '+user.username + \
            ' Use the link below to verify your email \n' + absurl
        data = {'email_body': email_body, 'to_email': user.email,
                'email_subject': 'Verify your email'}

        Util.send_email(data)
        return Response(user_data, status=status.HTTP_201_CREATED)
    
