from django.contrib import admin

from . import models


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id' , 'name')
    readonly_fields = ('id',)
    search_fields = ('name',)


@admin.register(models.Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'category', 'template', 'modified', 'deleted', 'description')
    list_filter = ('owner', 'category', 'deleted')
    readonly_fields = ('id',)


@admin.register(models.TemplateField)
class TemplateFieldAdmin(admin.ModelAdmin):
    list_display = ('id', 'template_id', 'tag', 'name', 'hint')
    list_filter = ('template_id',)
    readonly_fields = ('id',)
    search_fields = ('name',)


@admin.register(models.Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'template_id', 'user_id', 'created', 'completed', 'description')
    list_filter = ('template_id', 'user_id', 'completed')
    readonly_fields = ('id',)

@admin.register(models.DocumentField)
class DocumentFieldAdmin(admin.ModelAdmin):
    list_display = ('id', 'document_id', 'field_id', 'value', 'description')
    list_filter = ('document_id', 'field_id')
    readonly_fields = ('id',)
