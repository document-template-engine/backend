from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from core.constants import Messages

User = get_user_model()


class Category(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name="Наименование категории",
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Template(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name="Автор шаблона",
        null=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        verbose_name="Категория",
        null=True,
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
        ordering = ("name",)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.pk is not None:
            old_self = Template.objects.get(pk=self.pk)
            if old_self.template and self.template != old_self.template:
                # удаление старого файла шаблона
                old_self.template.delete(False)
        return super().save(*args, **kwargs)


class TemplateFieldGroup(models.Model):
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
        return self.name


class TemplateField(models.Model):
    template = models.ForeignKey(
        Template,
        on_delete=models.CASCADE,
        verbose_name="Шаблон",
        related_name="fields",
    )
    tag = models.CharField(max_length=255, verbose_name="Тэг поля")
    name = models.CharField(max_length=255, verbose_name="Наименование поля")
    hint = models.TextField(null=True, blank=True, verbose_name="Подсказка")
    group = models.ForeignKey(
        TemplateFieldGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Группа",
        help_text="Группа полей в шаблоне",
        related_name="fields",
    )

    class Meta:
        verbose_name = "Поле шаблона"
        verbose_name_plural = "Поля шаблона"
        ordering = ("name",)

    def __str__(self):
        return self.name

    def clean(self):
        # Запрет назначения группы, привязанной к другому шаблону
        if self.group and self.group.template != self.template:
            raise ValidationError(Messages.WRONG_FIELD_AND_GROUP_TEMPLATES)


class DocumentField(models.Model):
    field = models.ForeignKey(
        TemplateField, on_delete=models.CASCADE, verbose_name="Поле"
    )
    value = models.CharField(max_length=255, verbose_name="Содержимое поля")
    description = models.TextField(verbose_name="Описание поля")

    class Meta:
        verbose_name = "Поле документа"
        verbose_name_plural = "Поля документа"


class Document(models.Model):
    template = models.ForeignKey(
        Template, on_delete=models.CASCADE, verbose_name="Шаблон"
    )
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Автор документа"
    )
    created = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания"
    )
    completed = models.BooleanField(verbose_name="Документ заполнен")
    description = models.TextField(verbose_name="Описание документа")
    document_fields = models.ManyToManyField(
        DocumentField, through="FieldToDocument"
    )

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"
        ordering = ("created",)


class FieldToDocument(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    fields = models.ForeignKey(DocumentField, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Связь между полем и документом"
        verbose_name_plural = "Связи между полями и документами"

    def __str__(self):
        return f"{self.document} {self.fields}"


# class Object(models.Model):
# ''' Сущность которой '''
# user = models.ForeignKey(User, on_delete=models.CASCADE)


# class ObjectField(models.Model):
# template_field_id = models.ForeignKey(TemplateField, on_delete=models.CASCADE)
# object_id = models.ForeignKey(Object, on_delete=models.CASCADE)


class FavTemplate(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        null=True,
    )
    template = models.ForeignKey(
        to=Template,
        on_delete=models.CASCADE,
        verbose_name="Шаблон",
        null=True,
    )

    class Meta:
        verbose_name = "Избранный шаблон"
        verbose_name_plural = "Избранные шаблоны"
        constraints = (
            models.UniqueConstraint(
                fields=["user", "template"], name="unique_user_template"
            ),
        )

    def __str__(self):
        return f"{self.template} в избранном у {self.user}"


class FavDocument(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        null=True,
    )
    document = models.ForeignKey(
        to=Document,
        on_delete=models.CASCADE,
        verbose_name="Документ",
        null=True,
    )

    class Meta:
        verbose_name = "Избранный документ"
        verbose_name_plural = "Избранные документы"
        constraints = (
            models.UniqueConstraint(
                fields=["user", "document"], name="unique_user_document"
            ),
        )

    def __str__(self):
        return f"{self.document} в избранном у {self.user}"
