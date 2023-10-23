from api.v1.views import (
    AnonymousDownloadPreviewAPIView,
    DocumentFieldViewSet,
    DocumentViewSet,
    TemplateFieldViewSet,
    TemplateViewSet,
    FavTemplateAPIview,
    FavDocumentAPIview,
    RegisterView,
)
from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

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
    path("templates/<int:template_id>/favorite/", FavTemplateAPIview.as_view()),
    path("documents/<int:document_id>/favorite/", FavDocumentAPIview.as_view()),
    re_path(
        r"^templates/(?P<template_id>[^/.]+)/download_preview/$",
        AnonymousDownloadPreviewAPIView.as_view(),
        name="download_preview",
    ),
    path('users/', RegisterView.as_view(), name="register"),
    path("", include(router_v1.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
