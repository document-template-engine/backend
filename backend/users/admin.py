"""Настройка админки для пользователей."""

from django.contrib import admin
from django.contrib.auth.models import Group

from users.models import User


@admin.register(User)
class Users(admin.ModelAdmin):
    list_display = ("email", "username",)


admin.site.unregister(Group)
