from rest_framework import filters
from rest_framework import viewsets, serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django.http.response import StreamingHttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework import filters, status

from .serializers import (
    TemplateFieldSerializer,
    TemplateSerializer,
    DocumentReadSerializer,
    DocumentWriteSerializer,
    DocumentFieldSerializer,
    CategorySerializer,
    FavDocumentSerializer,
    FavTemplateSerializer,
    TemplateSerializerMinified,
)
from documents.models import (
    Document,
    DocumentField,
    Template,
    TemplateField,
    FavTemplate,
    FavDocument,
    Category
)
from core.template_render import DocumentTemplate


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

    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    http_method_names = ("get",)
    permissions_classes = (AllowAny,)
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    )
    pagination_class = None
    filterset_fields = ('owner', 'category',)
    search_fields = ('owner', 'category',)
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
        template = self.kwargs.get("template")
        template = get_object_or_404(Template, id=template)
        return template.fields.all()


class DocumentViewSet(viewsets.ModelViewSet):
    """Заглушка. Документ."""

    queryset = Document.objects.all()
    serializer_class = DocumentReadSerializer
    http_method_names = (
        'get',
        'post',
        'patch',
        'delete'
    )
    permissions_classes = (AllowAny,)
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    )
    pagination_class = None
    filterset_fields = ('owner',)
    search_fields = ('owner',)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"] and self.request.user.is_authenticated:
            return DocumentReadSerializer
        return DocumentWriteSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(
        detail=False,
        permission_classes=[AllowAny, ],
        url_path=r'draft'
    )
    def draft_documents(self, request):
        """Возвращает список незаконченных документов/черновиков"""
        user = self.request.user
        print(user)
        queryset = Document.objects.filter(completed=False, owner=user)
        serializer = DocumentReadSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(
        detail=False,
        permission_classes=[AllowAny, ],
        url_path=r'history'
    )
    def history_documents(self, request):
        """Возвращает список законченных документов/история"""
        user = self.request.user
        print(user)
        queryset = Document.objects.filter(completed=True, owner=user)
        serializer = DocumentReadSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        permission_classes=[
            AllowAny,
        ],
        url_path=r"download_document",
    )
    def download_document(self, request, pk=None):
        """ Пока говно код. Скачивание готового документа"""

        document = get_object_or_404(Document, id=pk)
        context = dict()
        field = DocumentField.objects.filter(document=pk)
        serializers =  DocumentFieldSerializer(field, many=True)
        for field in serializers.data:
            name_field = TemplateField.objects.get(id=field['field'])
            context[str(name_field)] = field['value']

        path = document.template.template
        doc = DocumentTemplate(path)
        buffer = doc.get_draft(context)

        response = StreamingHttpResponse(
            streaming_content=buffer,  
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        name = document.template.name
        response['Content-Disposition'] = f'attachment;filename={name}.docx'
        response["Content-Encoding"] = 'UTF-8'

        return response


class DocumentFieldViewSet(viewsets.ModelViewSet):
    """ Заглушка. Поле шаблона. """
    queryset = DocumentField.objects.all()
    serializer_class = DocumentFieldSerializer
    http_method_names = (
        'get',
        'post',
        'patch',
        'delete'
    )
    permissions_classes = (AllowAny,)


class FavTemplateViewSet(viewsets.ModelViewSet):
    http_method_names = ['post', 'delete']
    serializer_class = FavTemplateSerializer

    def get_queryset(self):
        template = self.kwargs.get('template')
        new_queryset = FavTemplate.objects.filter(template=template)
        return new_queryset

    @action(
        detail=False,
        methods=('delete',),
        permission_classes=IsAuthenticated,
        url_path='',
        url_name='favorite-delete',
    )
    def delete(self, request, *args, **kwargs):
        # стандартный viewset разрешает метод delete только на something/id/
        # поэтому если /something/something_else/, придётся @action писать
        template = self.kwargs.get('template')

        # проверка, что такой FavTemplate существует в БД
        queryset = FavTemplate.objects.filter(
            user=self.request.user, template=template
        )
        if len(queryset) == 0:
            raise serializers.ValidationError(
                'Этот шаблон отсутствует в Избранном!'
            )

        FavTemplate.objects.filter(template=template).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        template_id = self.kwargs.get('template')
        template = get_object_or_404(Template, id=template_id)

        # проверка, что такого FavTemplate уже нет в БД
        queryset = FavTemplate.objects.filter(
            user=self.request.user, template=template
        )
        if len(queryset) > 0:
            raise serializers.ValidationError(
                'Этот шаблон уже есть в Избранном!'
            )

        # запись нового объекта FavTemplate
        serializer.save(user=self.request.user, template=template)

        return Response(status=status.HTTP_201_CREATED)


class FavDocumentViewSet(viewsets.ModelViewSet):
    http_method_names = ['post', 'delete']
    serializer_class = FavDocumentSerializer

    def get_queryset(self):
        document = self.kwargs.get('document')
        new_queryset = FavDocument.objects.filter(document=document)
        return new_queryset

    @action(
        detail=False,
        methods=('delete',),
        permission_classes=IsAuthenticated,
        url_path='',
        url_name='favorite-delete',
    )
    def delete(self, request, *args, **kwargs):
        # стандартный viewset разрешает метод delete только на something/id/
        # поэтому если /something/something_else/, придётся @action писать
        document = self.kwargs.get('document')

        # проверка, что такой FavTemplate существует в БД
        queryset = FavDocument.objects.filter(
            user=self.request.user, document=document
        )
        if len(queryset) == 0:
            raise serializers.ValidationError(
                'Этот документ отсутствует в Избранном!'
            )

        FavTemplate.objects.filter(document=document).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        document_id = self.kwargs.get('document')
        document = get_object_or_404(Document, id=document_id)

        # проверка, что такого FavTemplate уже нет в БД
        queryset = FavDocument.objects.filter(
            user=self.request.user, document=document
        )
        if len(queryset) > 0:
            raise serializers.ValidationError(
                'Этот документ уже есть в Избранном!'
            )

        # запись нового объекта FavTemplate
        serializer.save(user=self.request.user, document=document)

        return Response(status=status.HTTP_201_CREATED)
