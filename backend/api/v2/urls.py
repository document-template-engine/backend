from api.v2.documents.views import (
    AnonymousDownloadPreviewAPIView,
    DocumentFieldViewSet,
    DocumentViewSet,)
from api.v2.templates.views import (
    UploadTemplateFileAPIView,
    CheckTemplateConsistencyAPIView,
    TemplateFieldViewSet,
    TemplateViewSet,)
from api.v2.favorites.views import (
    FavTemplateAPIview,
    FavDocumentAPIview,)
from api.v2.objects.views import (
    BaseObjectViewSet,
    BaseObjectFieldViewSet,
    ObjectViewSet,
    ObjectFieldViewSet
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

router_v1.register(
    prefix="base_objects",
    basename="base_objects",
    viewset=BaseObjectViewSet,
)
router_v1.register(
    prefix="base_object_fields",
    basename="base_object_fields",
    viewset=BaseObjectFieldViewSet,
)
router_v1.register(
    prefix="objects",
    basename="objects",
    viewset=ObjectViewSet,
)
router_v1.register(
    prefix="object_fields",
    basename="object_fields",
    viewset=ObjectFieldViewSet,
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
    path("", include(router_v1.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
