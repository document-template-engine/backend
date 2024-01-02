from api.v1.views import (
    AnonymousDownloadPreviewAPIView,
    CheckTemplateConsistencyAPIView,
    DocumentFieldViewSet,
    DocumentViewSet,
    TemplateFieldViewSet,
    TemplateViewSet,
    FavTemplateAPIview,
    FavDocumentAPIview,
    UploadTemplateFileAPIView,
    # RegisterView,
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
    r"templates/(?P<template_id>[0-9]+)/fields",
    basename="template_fields",
    viewset=TemplateFieldViewSet,
)

router_v1.register(
    r"documents/(?P<document_id>[0-9]+)/fields",
    basename="document_fields",
    viewset=DocumentFieldViewSet,
)

router_v1.register(
    prefix="documents",
    basename="documents",
    viewset=DocumentViewSet,
)

urlpatterns = [
    path(
        "templates/<int:template_id>/favorite/", FavTemplateAPIview.as_view()
    ),
    path(
        "documents/<int:document_id>/favorite/", FavDocumentAPIview.as_view()
    ),
    path(
        "templates/<int:template_id>/download_preview/",
        AnonymousDownloadPreviewAPIView.as_view(),
        name="download_preview",
    ),
    path(
        "templates/<int:template_id>/check_consistency/",
        CheckTemplateConsistencyAPIView.as_view(),
        name="check_consistency",
    ),
    re_path(
        "templates/<int:template_id>/upload_template/",
        UploadTemplateFileAPIView.as_view(),
        name="upload_template",
    ),
    # path("users/", RegisterView.as_view(), name="register"),
    path("", include(router_v1.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
