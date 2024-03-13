"""Модели документов."""
from typing import List, Tuple

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from core.constants import Messages
from core.template_render import DocumentTemplate
from base_objects.models import (
    BaseObject,
    BaseObjectField,
)

User = get_user_model()


class Category(models.Model):
    """Категории шаблона."""

    name = models.CharField(
        max_length=255,
        verbose_name="Наименование категории",
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ("name",)

    def __str__(self):
        """Отображение - название."""
        return self.name


class Template(models.Model):
    """Шаблоны документа."""

    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name="Автор шаблона",
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        verbose_name="Категория",
        null=True,
        blank=True,
    )
    template = models.FileField(
        upload_to="templates/", verbose_name="Файл шаблона"
    )
    name = models.CharField(
        max_length=255, verbose_name="Наименование шаблона"
    )
    updated = models.DateTimeField(
        verbose_name="Дата изменения", auto_now=True
    )
    deleted = models.BooleanField(verbose_name="Удален")
    description = models.TextField(verbose_name="Описание шаблона")
    image = models.ImageField(
        "Картинка",
        upload_to="posts/",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Шаблон"
        verbose_name_plural = "Шаблоны"
        default_related_name = "templates"
        ordering = ("name",)

    def __str__(self):
        """Отображение - название."""
        return self.name

    def save(self, *args, **kwargs):
        """Удаление старого файла шаблона при сохранении."""
        if self.pk is not None:
            old_self = Template.objects.get(pk=self.pk)
            if old_self.template and self.template != old_self.template:
                # удаление старого файла шаблона
                try:
                    old_self.template.delete(False)
                except Exception as e:
                    print(e)
        return super().save(*args, **kwargs)

    def get_inconsistent_tags(self) -> Tuple[Tuple, Tuple]:
        """
        Возвращает списки несогласованных тэгов между БД и шаблоном docx.

        :returns: (excess_tags, excess_fields)
        excess_tags - кортеж тэгов, которые имеются в docx, но отсутствуют в БД.
        excess_fields - кортеж тэгов, которые имеются в БД, но отсутствуют в docx.
        """
        docx_tags, field_tags = set(), set()
        if self.template:
            try:
                doc = DocumentTemplate(self.template)
                docx_tags = set(doc.get_tags())
            except Exception as e:
                print(e)  # TODO: add logging

        field_tags = {field.tag for field in self.fields.all()}
        excess_tags = tuple(docx_tags - field_tags)
        excess_fields = tuple(field_tags - docx_tags)
        return (excess_tags, excess_fields)

    def get_consistency_errors(self) -> List:
        """Генерирует ответ в зависимости от согласованности полей шаблона."""

        excess_tags, excess_fields = self.get_inconsistent_tags()
        errors = []
        if excess_tags:
            errors.append(
                {"message": Messages.TEMPLATE_EXCESS_TAGS, "tags": excess_tags}
            )
        if excess_fields:
            errors.append(
                {
                    "message": Messages.TEMPLATE_EXCESS_FIELDS,
                    "tags": excess_fields,
                }
            )
        return errors


class TemplateFieldGroup(models.Model):
    """Группы полей шаблона."""

    template = models.ForeignKey(
        Template,
        on_delete=models.CASCADE,
        verbose_name="Шаблон",
        related_name="field_groups",
    )
    name = models.CharField(
        max_length=255,
        verbose_name="Наименование группы полей",
    )

    type_object = models.ForeignKey(
        BaseObject,
        on_delete=models.SET_NULL,
        verbose_name="Обьект",
        null=True,
        blank=True,
        # default=None
    )

    class Meta:
        verbose_name = "Группа полей"
        verbose_name_plural = "Группы полей"
        ordering = ("id",)

    def __str__(self):
        """Отображение - название."""
        return self.name


class TemplateFieldType(models.Model):
    """Типы полей шаблонов документов."""

    type = models.SlugField(verbose_name="Тип данных", unique=True)
    name = models.CharField(max_length=50, verbose_name="Наименование типа")
    mask = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Маска допустимых значений",
    )

    class Meta:
        verbose_name = "Тип поля шаблона"
        verbose_name_plural = "Типы поля шаблона"
        ordering = ("name",)

    def __str__(self):
        """Отображение - название (тип поля)."""
        return f"{self.name} ({self.type})"


class TemplateField(models.Model):
    """Поля шаблона."""

    template = models.ForeignKey(
        Template,
        on_delete=models.CASCADE,
        verbose_name="Шаблон",
    )
    base_object_field = models.ForeignKey(
        BaseObjectField,
        on_delete=models.SET_NULL,
        verbose_name="Поле базового обьекта",
        null=True,
        blank=True,
        default=1
    )
    tag = models.CharField(max_length=255, verbose_name="Тэг поля")
    name = models.CharField(max_length=255, verbose_name="Наименование поля")
    hint = models.CharField(
        max_length=255, blank=True, verbose_name="Подсказка"
    )
    group = models.ForeignKey(
        TemplateFieldGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Группа",
        help_text="Группа полей в шаблоне",
    )
    type = models.ForeignKey(
        TemplateFieldType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Тип",
        help_text="Тип поля",
    )
    length = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Размер поля ввода"
    )
    default = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Значение по умолчанию",
    )

    class Meta:
        verbose_name = "Поле шаблона"
        verbose_name_plural = "Поля шаблона"
        default_related_name = "fields"
        ordering = ("template", "name")

    def __str__(self):
        """Отображение - название поля (шаблон)."""
        return f"{self.name} ({self.template})"

    def clean(self):
        """Запрет назначения группы, привязанной к другому шаблону."""
        if self.group and self.group.template != self.template:
            raise ValidationError(Messages.WRONG_FIELD_AND_GROUP_TEMPLATES)


class Document(models.Model):
    """Документ."""

    template = models.ForeignKey(
        Template, on_delete=models.PROTECT, verbose_name="Шаблон"
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор документа",
        null=True,
        blank=True,
    )
    created = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания"
    )
    updated = models.DateTimeField(
        auto_now=True, verbose_name="Дата изменения"
    )
    completed = models.BooleanField(
        verbose_name="Документ заполнен", default=False
    )
    description = models.TextField(verbose_name="Описание документа")

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"
        ordering = ("created",)
        default_related_name = "documents"

    def __str__(self):
        """Автор документа и название шаблона."""
        return f"{self.owner} {self.template}"

    def create_document_fields(self, fields_data):
        """Создание полей для данного документа по данным из fields_data"""
        document_fields = []
        for field_data in fields_data:
            template_field = field_data["field"]
            template = TemplateField.objects.get(id=template_field.id).template
            if self.template == template:
                # Проверяется, принадлежит ли поле шаблону документа
                document_fields.append(
                    DocumentField(
                        field=template_field,
                        value=field_data["value"],
                        document=self,
                    )
                )
        DocumentField.objects.bulk_create(document_fields)


class DocumentField(models.Model):
    """Поля документа."""

    field = models.ForeignKey(
        TemplateField,
        on_delete=models.PROTECT,
        verbose_name="Поле",
        related_name="document_fields",
    )
    value = models.CharField(max_length=255, verbose_name="Содержимое поля")
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        verbose_name="Документ",
        related_name="document_fields",
    )

    class Meta:
        verbose_name = "Поле документа"
        verbose_name_plural = "Поля документа"
        ordering = ("field__template", "field")

    def __str__(self):
        """Отображение - шаблон поле."""
        return f"{self.field.template} {self.field}"


class FavTemplate(models.Model):
    """Избранные шаблоны."""

    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    template = models.ForeignKey(
        to=Template,
        on_delete=models.CASCADE,
        verbose_name="Шаблон",
    )

    class Meta:
        verbose_name = "Избранный шаблон"
        verbose_name_plural = "Избранные шаблоны"
        constraints = (
            models.UniqueConstraint(
                fields=("user", "template"), name="unique_user_template"
            ),
        )
        default_related_name = "favorite_templates"
        ordering = ("user", "template")

    def __str__(self):
        """Строковое отображение."""
        return f"{self.template} в избранном у {self.user}"


class FavDocument(models.Model):
    """Избранные документы."""

    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    document = models.ForeignKey(
        to=Document,
        on_delete=models.CASCADE,
        verbose_name="Документ",
    )

    class Meta:
        verbose_name = "Избранный документ"
        verbose_name_plural = "Избранные документы"
        constraints = (
            models.UniqueConstraint(
                fields=("user", "document"), name="unique_user_document"
            ),
        )
        default_related_name = "favorite_documents"
        ordering = ("user", "document")

    def __str__(self):
        """Строковое отображение."""
        return f"{self.document} в избранном у {self.user}"
