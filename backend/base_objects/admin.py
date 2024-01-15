"""Настройки админки для приложения "Документы"."""
from django.contrib import admin

from base_objects import models

@admin.register(models.BaseObject)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(models.BaseObjectField)
class ObjectFieldAdmin(admin.ModelAdmin):
    list_display = ("id", "name")

@admin.register(models.Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(models.ObjectField)
class ObjectFieldAdmin(admin.ModelAdmin):
    list_display = ("id", "value")

