"""Вьюсеты v1 API."""
import logging

from django.contrib.auth import get_user_model
from rest_framework import (
    serializers,
    status,
)

from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    FavDocumentSerializer,
    FavTemplateSerializer,
)
from documents.models import (
    FavDocument,
    FavTemplate,
)

logger = logging.getLogger(__name__)

User = get_user_model()


class FavTemplateAPIview(APIView):
    permission_classes = (IsAuthenticated,)
    # permission_classes = (AllowAny,) # Заглушка

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
    # permission_classes = (AllowAny,) # Заглушка

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
