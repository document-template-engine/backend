"""Модели обьектов."""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseObject(models.Model):
    """Шаблон обьекта."""

    name = models.CharField(
        max_length=255,
        verbose_name="Наименование базового обьекта"
    )
    updated = models.DateTimeField(
        verbose_name="Дата изменения",
        auto_now=True
    )
    deleted = models.BooleanField(verbose_name="Удален")
    description = models.TextField(verbose_name="Описание базового обьекта")

    class Meta:
        verbose_name = "базовый Обьекта"
        verbose_name_plural = "базовые Обьекты"
        default_related_name = "Base_objects"
        ordering = ("name",)

    def __str__(self):
        """Отображение - название."""
        return self.name


class BaseObjectField(models.Model):
    """Поля шаблон обьектов"""

    base_object = models.ForeignKey(
        BaseObject,
        on_delete=models.CASCADE,
        verbose_name="поля базового Обьект",
        default=1,
    )
    name = models.CharField(
        max_length=255,
        verbose_name="Наименование базового поля обьекта")

    class Meta:
        verbose_name = "Поле базового обьекта"
        verbose_name_plural = "Поля базового обьекта"
        default_related_name = "base_fields"

    def __str__(self):
        """Отображение - название поля (базового обьекта)."""
        return f"{self.name} ({self.base_object})"


class Object(models.Model):
    """Обьект."""

    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name="Автор документа",
        null=True,
        blank=True,
    )
    base_object = models.ForeignKey(
        BaseObject,
        on_delete=models.CASCADE,
        verbose_name="Базовый Обьект",
        null=True,
        blank=True,
    )
    name = models.CharField(
        max_length=255, verbose_name="Наименование обьекта"
    )
    created = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата создания"
    )
    updated = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата изменения"
    )

    class Meta:
        verbose_name = "Обьект"
        verbose_name_plural = "Обьекты"
        default_related_name = "customer_objects"

    def __str__(self):
        """Отображение - название."""
        return self.name


class ObjectField(models.Model):
    """Поля обьекта"""

    object = models.ForeignKey(
        Object,
        on_delete=models.CASCADE,
        verbose_name="Обьект",
    )
    base_field = models.ForeignKey(
        BaseObjectField,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Поле",
        related_name="object_fields",
    )
    value = models.CharField(
        max_length=255,
        verbose_name="Содержимое поля",
        blank=True,
        null=True,)

    class Meta:
        verbose_name = "Поле обьекта"
        verbose_name_plural = "Поля обьекта"

    def __str__(self):
        """Отображение - название поля (шаблон)."""
        return f"{self.value}"
