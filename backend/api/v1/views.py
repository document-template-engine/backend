from rest_framework import filters
from rest_framework import viewsets, serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.http.response import StreamingHttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import (
    TemplateSerializer,
    DocumentSerializer,
    DocumentFieldSerializer,
    CategorySerializer,
    FavDocumentSerializer,
    FavTemplateSerializer
)
from documents.models import (
    Document,
    DocumentField,
    Template,
    TemplateField,
    FavTemplate,
    Category
)
from core.template_render import DocumentTemplate


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permissions_classes = (AllowAny,)


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

    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    )
    pagination_class = None
    filterset_fields = ('owner', 'category',)
    search_fields = ('owner', 'category',)


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

    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    )
    pagination_class = None
    filterset_fields = ('user_id',)
    search_fields = ('user_id',)

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


class FavTemplateViewSet(viewsets.ModelViewSet):
    http_method_names = ['post', 'delete']
    serializer_class = FavTemplateSerializer

    def get_queryset(self):
        template_id = self.kwargs.get('template_id')
        new_queryset = FavTemplate.objects.filter(template_id=template_id)
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
        template_id = self.kwargs.get('template_id')

        # проверка, что такой FavTemplate существует в БД
        queryset = FavTemplate.objects.filter(
            user_id=self.request.user, template_id=template_id
        )
        if len(queryset) == 0:
            raise serializers.ValidationError(
                'Этот шаблон отсутствует в Избранном!'
            )

        FavTemplate.objects.filter(template_id=template_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        template_id = self.kwargs.get('template_id')
        template = get_object_or_404(Template, id=template_id)

        # проверка, что такого FavTemplate уже нет в БД
        queryset = FavTemplate.objects.filter(
            user_id=self.request.user, template_id=template_id
        )
        if len(queryset) > 0:
            raise serializers.ValidationError(
                'Этот шаблон уже есть в Избранном!'
            )

        # запись нового объекта FavTemplate
        serializer.save(user_id=self.request.user, template_id=template)

        return Response(status=status.HTTP_201_CREATED)


class FavDocumentViewSet(viewsets.ModelViewSet):
    http_method_names = ['post', 'delete']
    serializer_class = FavDocumentSerializer

    def get_queryset(self):
        document_id = self.kwargs.get('document_id')
        new_queryset = FavTemplate.objects.filter(document_id=document_id)
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
        document_id = self.kwargs.get('document_id')

        # проверка, что такой FavTemplate существует в БД
        queryset = FavTemplate.objects.filter(
            user_id=self.request.user, document_id=document_id
        )
        if len(queryset) == 0:
            raise serializers.ValidationError(
                'Этот документ отсутствует в Избранном!'
            )

        FavTemplate.objects.filter(document_id=document_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        document_id = self.kwargs.get('document_id')
        document = get_object_or_404(Document, id=document_id)

        # проверка, что такого FavTemplate уже нет в БД
        queryset = FavTemplate.objects.filter(
            user_id=self.request.user, document_id=document_id
        )
        if len(queryset) > 0:
            raise serializers.ValidationError(
                'Этот документ уже есть в Избранном!'
            )

        # запись нового объекта FavTemplate
        serializer.save(user_id=self.request.user, document_id=document)

        return Response(status=status.HTTP_201_CREATED)
