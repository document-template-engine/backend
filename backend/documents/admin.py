"""Настройки админки для приложения "Документы"."""
from django import forms
from django.contrib import admin

from documents import models


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    readonly_fields = ("id",)
    search_fields = ("name",)


@admin.register(models.FavDocument)
class FavDocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "document")
    readonly_fields = ("id",)
    search_fields = ("user",)


@admin.register(models.FavTemplate)
class FavTemplateAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "template")
    readonly_fields = ("id",)
    search_fields = ("user",)


class TemplateFieldInlineAdmin(admin.TabularInline):
    model = models.TemplateField
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "group" and request._template_instance_:
            kwargs["queryset"] = models.TemplateFieldGroup.objects.filter(
                template=request._template_instance_
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "default":
            formfield.strip = False
        return formfield


@admin.register(models.Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "owner",
        "category",
        "template",
        "updated",
        "deleted",
        "description",
        "image",
    )
    list_filter = ("owner", "category", "deleted")
    readonly_fields = ("id", "updated")
    inlines = (TemplateFieldInlineAdmin,)

    def get_form(self, request, instance=None, **kwargs):
        request._template_instance_ = instance
        return super().get_form(request, instance, **kwargs)


@admin.register(models.TemplateFieldGroup)
class TemplateFieldGroupAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "template",)
    readonly_fields = ("id",)
    search_fields = ("name", "template")


@admin.register(models.TemplateFieldType)
class TemplateFieldTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "name", "mask")
    readonly_fields = ("id",)
    search_fields = ("name",)


class TemplateFieldForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # allow space for default value
        self.fields["default"].strip = False

    class Meta:
        model = models.TemplateField
        fields = "__all__"


@admin.register(models.TemplateField)
class TemplateFieldAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "template",
        "tag",
        "name",
        "hint",
        "group",
        "type",
        "length",
        # "base_object_field",
    )
    list_filter = ("template",)
    readonly_fields = ("id",)
    search_fields = ("name",)

    form = TemplateFieldForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "group":
            field_id = request.resolver_match.kwargs.get("object_id")
            if field_id:
                field = models.TemplateField.objects.get(id=field_id)
                if field.template:
                    kwargs[
                        "queryset"
                    ] = models.TemplateFieldGroup.objects.filter(
                        template=field.template
                    )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class DocumentFieldInlineAdmin(admin.TabularInline):
    model = models.DocumentField
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "field" and request._document_instance_:
            template = request._document_instance_.template
            if template:
                kwargs["queryset"] = template.fields.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(models.Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "template",
        "owner",
        "created",
        "updated",
        "completed",
        "description",
    )
    list_filter = ("template", "owner", "completed")
    readonly_fields = ("id", "created", "updated")
    inlines = (DocumentFieldInlineAdmin,)

    def get_form(self, request, instance=None, **kwargs):
        request._document_instance_ = instance
        return super().get_form(request, instance, **kwargs)


@admin.register(models.DocumentField)
class DocumentFieldAdmin(admin.ModelAdmin):
    list_display = ("id", "document_id", "field_id", "value")
    readonly_fields = ("id",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "field":
            docfield_id = request.resolver_match.kwargs.get("object_id")
            if docfield_id:
                docfield = models.DocumentField.objects.get(id=docfield_id)
                if docfield.document.template:
                    kwargs[
                        "queryset"
                    ] = docfield.document.template.fields.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.site_header = "Административная панель Шаблонизатор"
admin.site.index_title = "Настройки Шаблонизатор"
admin.site.site_title = "Административная панель Шаблонизатор"
