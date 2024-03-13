from rest_framework import (
    viewsets,
)

from base_objects.models import (
    BaseObject,
    Object,
    BaseObjectField,
    ObjectField
    )
from .serializers import (
    BaseObjectSerializer,
    BaseObjectFieldSerializer,
    ObjectSerializer,
    ObjectFieldSerializer,
)


class BaseObjectViewSet(viewsets.ModelViewSet):
    queryset = BaseObject.objects.all()
    serializer_class = BaseObjectSerializer


class BaseObjectFieldViewSet(viewsets.ModelViewSet):
    queryset = BaseObjectField.objects.all()
    serializer_class = BaseObjectFieldSerializer


class ObjectViewSet(viewsets.ModelViewSet):
    queryset = Object.objects.all()
    serializer_class = ObjectSerializer


class ObjectFieldViewSet(viewsets.ModelViewSet):
    queryset = ObjectField.objects.all()
    serializer_class = ObjectFieldSerializer