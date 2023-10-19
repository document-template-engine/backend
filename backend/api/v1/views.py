from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, serializers, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsOwnerOrAdminOrReadOnly
from .serializers import (
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


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permissions_classes = (AllowAny,)


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
        """Скачивание готового документа"""

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


class DocumentFieldViewSet(viewsets.ModelViewSet):
    """Заглушка. Поле шаблона."""

    queryset = DocumentField.objects.all()
    serializer_class = DocumentFieldSerializer
    http_method_names = ("get",)
    permissions_classes = (IsOwnerOrAdminOrReadOnly,)
    pagination_class = None

    def get_queryset(self):
        document_id = self.kwargs.get("document_id")
        document = get_object_or_404(Document, id=document_id)
        through_set = FieldToDocument.objects.filter(document=document).all()
        return DocumentField.objects.filter(fieldtodocument__in=through_set)


class FavTemplateViewSet(viewsets.ModelViewSet):
    http_method_names = ["post", "delete"]
    serializer_class = FavTemplateSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        template_id = self.kwargs.get("template_id")
        new_queryset = FavTemplate.objects.filter(template=template_id)
        return new_queryset

    @action(
        detail=False,
        methods=("delete",),
        url_path="",
        url_name="favorite-delete",
    )
    def delete(self, request, *args, **kwargs):
        # стандартный viewset разрешает метод delete только на something/id/
        # поэтому если /something/something_else/, придётся @action писать
        template_id = self.kwargs.get("template_id")

        # проверка, что такой FavTemplate существует в БД
        queryset = FavTemplate.objects.filter(
            user=self.request.user, template=template_id
        )
        if not queryset.exists():
            raise serializers.ValidationError(
                "Этот шаблон отсутствует в Избранном!"
            )
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        template_id = self.kwargs.get("template_id")
        template = get_object_or_404(Template, id=template_id)

        # проверка, что такого FavTemplate уже нет в БД
        queryset = FavTemplate.objects.filter(
            user=self.request.user, template=template
        )
        if queryset.exists():
            raise serializers.ValidationError(
                "Этот шаблон уже есть в Избранном!"
            )

        # запись нового объекта FavTemplate
        serializer.save(user=self.request.user, template=template)

        return Response(status=status.HTTP_201_CREATED)


class FavDocumentViewSet(viewsets.ModelViewSet):
    http_method_names = ["post", "delete"]
    serializer_class = FavDocumentSerializer
    permission_classes = ((IsAuthenticated,),)

    def get_queryset(self):
        document_id = self.kwargs.get("document_id")
        new_queryset = FavDocument.objects.filter(document=document_id)
        return new_queryset

    @action(
        detail=False,
        methods=("delete",),
        url_path="",
        url_name="favorite-delete",
    )
    def delete(self, request, *args, **kwargs):
        # стандартный viewset разрешает метод delete только на something/id/
        # поэтому если /something/something_else/, придётся @action писать
        document = self.kwargs.get("document")

        # проверка, что такой FavTemplate существует в БД
        queryset = FavDocument.objects.filter(
            user=self.request.user, document=document
        )
        if not queryset.exists():
            raise serializers.ValidationError(
                "Этот документ отсутствует в Избранном!"
            )
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        document_id = self.kwargs.get("document")
        document = get_object_or_404(Document, id=document_id)

        # проверка, что такого Fav уже нет в БД
        queryset = FavDocument.objects.filter(
            user=self.request.user, document=document
        )
        if queryset.exists():
            raise serializers.ValidationError(
                "Этот документ уже есть в Избранном!"
            )

        # запись нового объекта Fav
        serializer.save(user=self.request.user, document=document)

        return Response(status=status.HTTP_201_CREATED)


class FavTemplateAPIview(APIView):
    def post(self, request, **kwargs):
        data = {
            "user": self.request.user.pk,
            "template": self.kwargs.get("template_id")
        }
        serializer = FavTemplateSerializer(data=data)
        queryset = FavTemplate.objects.filter(
            user=self.request.user.pk,
            template=self.kwargs.get("template_id")
        )
        # проверка, что такого FavTemplate нет в БД
        if len(queryset) > 0:
            raise serializers.ValidationError(
                "Этот шаблон уже есть в Избранном!"
            )
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        queryset = FavTemplate.objects.filter(
            user=self.request.user.pk,
            template=self.kwargs.get("template_id")
        )
        # проверка, что такой FavTemplate существует в БД
        if len(queryset) == 0:
            raise serializers.ValidationError(
                "Этот шаблон отсутствует в Избранном!"
            )
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavDocumentAPIview(APIView):
    def post(self, request, **kwargs):
        data = {
            "user": self.request.user.pk,
            "document": self.kwargs.get("document_id")
        }
        serializer = FavDocumentSerializer(data=data)
        queryset = FavDocument.objects.filter(
            user=self.request.user.pk,
            document=self.kwargs.get("document_id")
        )
        # проверка, что такого FavDocument нет в БД
        if len(queryset) > 0:
            raise serializers.ValidationError(
                "Этот документ уже есть в Избранном!"
            )
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        queryset = FavDocument.objects.filter(
            user=self.request.user.pk,
            document=self.kwargs.get("document_id")
        )
        # проверка, что такой FavDocument существует в БД
        if len(queryset) == 0:
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
