from django.contrib.auth import get_user_model
from django.db import models

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


class Document(models.Model):
    template_id = models.ForeignKey(
        Template, on_delete=models.CASCADE, verbose_name="Шаблон"
    )
    user_id = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Автор документа"
    )
    created = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания"
    )
    completed = models.BooleanField(verbose_name="Документ заполнен")
    description = models.TextField(verbose_name="Описание документа")

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"
        ordering = ("created",)


class TemplateField(models.Model):
    template_id = models.ForeignKey(
        Template,
        on_delete=models.CASCADE,
        verbose_name="Шаблон",
        related_name="fields",
    )
    tag = models.CharField(max_length=255, verbose_name="Тэг поля")
    name = models.CharField(max_length=255, verbose_name="Наименование поля")
    hint = models.TextField(null=True, blank=True, verbose_name="Подсказка")

    class Meta:
        verbose_name = "Поле шаблона"
        verbose_name_plural = "Поля шаблона"
        ordering = ("name",)

    def __str__(self):
        return self.name


class DocumentField(models.Model):
    document_id = models.ForeignKey(
        Document, on_delete=models.CASCADE, verbose_name="Документ"
    )
    field_id = models.ForeignKey(
        TemplateField, on_delete=models.CASCADE, verbose_name="Поле"
    )
    value = models.CharField(max_length=255, verbose_name="Содержимое поля")
    description = models.TextField(verbose_name="Описание поля")

    class Meta:
        verbose_name = "Поле документа"
        verbose_name_plural = "Поля документа"


# class Object(models.Model):
# ''' Сущность которой '''
# user = models.ForeignKey(User, on_delete=models.CASCADE)


# class ObjectField(models.Model):
# template_field_id = models.ForeignKey(TemplateField, on_delete=models.CASCADE)
# object_id = models.ForeignKey(Object, on_delete=models.CASCADE)
