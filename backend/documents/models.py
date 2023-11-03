"""Модели документов."""
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from core.constants import Messages

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
    template = models.FileField(upload_to="templates/")
    name = models.CharField(
        max_length=255, verbose_name="Наименование шаблона"
    )
    modified = models.DateField(verbose_name="Дата модификации", auto_now=True)
    deleted = models.BooleanField(verbose_name="Удален")
    description = models.TextField(verbose_name="Описание шаблона")

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


class DocumentField(models.Model):
    """Поля документа."""

    field = models.ForeignKey(
        TemplateField,
        on_delete=models.PROTECT,
        verbose_name="Поле",
        related_name="document_fields",
    )
    value = models.CharField(max_length=255, verbose_name="Содержимое поля")
    description = models.TextField(verbose_name="Описание поля", blank=True)

    class Meta:
        verbose_name = "Поле документа"
        verbose_name_plural = "Поля документа"
        ordering = ("field__template", "field")

    def __str__(self):
        """Отображение - шаблон поле."""
        return f"{self.field.template} {self.field}"


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
    document_fields = models.ManyToManyField(
        DocumentField, through="FieldToDocument"
    )

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"
        ordering = ("created",)
        default_related_name = "documents"

    def __str__(self):
        """Автор документа и название шаблона."""
        return f"{self.owner} {self.template}"


class FieldToDocument(models.Model):
    """Связь полей и документов."""

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="document_of_field",
    )
    fields = models.ForeignKey(
        DocumentField,
        on_delete=models.CASCADE,
        related_name="fields_of_document",
    )

    class Meta:
        verbose_name = "Связь между полем и документом"
        verbose_name_plural = "Связи между полями и документами"

    def __str__(self):
        return f"{self.document} {self.fields}"


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
