from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.views import (
    DocumentViewSet,
    FavDocumentViewSet,
    FavTemplateViewSet,
    TemplateViewSet,
    DocumentFieldViewSet,
    TemplateFieldViewSet,
)

app_name = "api"

router_v1 = DefaultRouter()

router_v1.register(
    prefix="templates",
    basename="templates",
    viewset=TemplateViewSet,
)

router_v1.register(
    r"templates/(?P<template_id>[^/.]+)/fields",
    basename="fields",
    viewset=TemplateFieldViewSet,
)

router_v1.register(
    r"templates/(?P<template_id>[^/.]+)/favorite",
    basename="template_favorites",
    viewset=FavTemplateViewSet,
)

router_v1.register(
    r"documents/(?P<document_id>[^/.]+)/favorite",
    basename="document_favorites",
    viewset=FavDocumentViewSet,
)

router_v1.register(
    prefix="documents",
    basename="documents",
    viewset=DocumentViewSet,
)

router_v1.register(
    r"documents/(?P<document_id>[^/.]+)/fields",
    basename="fields",
    viewset=DocumentFieldViewSet,
)

urlpatterns = [
    path("", include(router_v1.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
