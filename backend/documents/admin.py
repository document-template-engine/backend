from django.contrib import admin

from . import models


admin.site.register(models.FieldToDocument)

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
    list_display = ('id', 'template_id', 'owner', 'created', 'completed', 'description')
    list_filter = ('template_id', 'owner', 'completed')
    readonly_fields = ('id',)

@admin.register(models.DocumentField)
class DocumentFieldAdmin(admin.ModelAdmin):
    list_display = ('id', 'field_id', 'value', 'description')
    readonly_fields = ('id',)


