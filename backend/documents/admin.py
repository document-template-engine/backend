from django.contrib import admin

from . import models

admin.site.register(models.FieldToDocument)


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


@admin.register(models.Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "owner",
        "category",
        "template",
        "modified",
        "deleted",
        "description",
    )
    list_filter = ("owner", "category", "deleted")
    readonly_fields = ("id",)
    inlines = (TemplateFieldInlineAdmin,)

    def get_form(self, request, instance=None, **kwargs):
        request._template_instance_ = instance
        return super().get_form(request, instance, **kwargs)


@admin.register(models.TemplateFieldGroup)
class TemplateFieldGroupAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "template")
    readonly_fields = ("id",)
    search_fields = ("name", "template")


@admin.register(models.TemplateField)
class TemplateFieldAdmin(admin.ModelAdmin):
    list_display = ("id", "template", "tag", "name", "hint", "group")
    list_filter = ("template",)
    readonly_fields = ("id",)
    search_fields = ("name",)

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


@admin.register(models.DocumentField)
class DocumentFieldAdmin(admin.ModelAdmin):
    list_display = ("id", "field_id", "value", "description")
    readonly_fields = ("id",)


admin.site.site_header = "Административная панель Шаблонизатор"
admin.site.index_title = "Настройки Шаблонизатор"
admin.site.site_title = "Административная панель Шаблонизатор"
