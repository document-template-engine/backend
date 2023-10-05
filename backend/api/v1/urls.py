from django.urls import include, path
from rest_framework.routers import DefaultRouter

from backend.api.v1.views import (
    DocumentViewSet,
    TemplateViewSet,
    DocumentFieldViewSet,
    TemplateFieldViewSet,
)

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register(
    prefix='templates',
    basename='templates',
    viewset=TemplateViewSet,
)

router_v1.register(
    prefix='templates/fields',
    basename='fields',
    viewset=TemplateFieldViewSet,
)

router_v1.register(
    prefix='documents',
    basename='documents',
    viewset=DocumentViewSet,
)

router_v1.register(
    prefix='documents/fields',
    basename='fields',
    viewset=DocumentFieldViewSet,
)

urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
