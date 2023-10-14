from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Category(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Наименование категории',
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Template(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор шаблона'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='Категория'
    )
    template = models.FileField(upload_to='templates/')
    name = models.CharField(max_length=255, verbose_name='Наименование шаблона')
    modified = models.DateField(verbose_name='Дата модификации')
    deleted = models.BooleanField(verbose_name='Удален')
    description = models.TextField(verbose_name='Описание шаблона')

    class Meta:
        verbose_name = 'Шаблон'
        verbose_name_plural = 'Шаблоны'
        ordering = ('name',)

    def __str__(self):
        return self.name


class TemplateField(models.Model):
    template_id = models.ForeignKey(Template, on_delete=models.CASCADE, verbose_name='Шаблон')
    tag = models.CharField(max_length=255, verbose_name='Тэг поля')
    name = models.CharField(max_length=255, verbose_name='Наименование поля')
    hint = models.TextField(null=True, blank=True, verbose_name='Подсказка')

    class Meta:
        verbose_name = 'Поле шаблона'
        verbose_name_plural = 'Поля шаблона'
        ordering = ('name',)

    def __str__(self):
        return self.name


class DocumentField(models.Model):
    field_id = models.ForeignKey(TemplateField, on_delete=models.CASCADE, verbose_name='Поле')
    value = models.CharField(max_length=255, verbose_name='Содержимое поля')
    description = models.TextField(default='Нет описания',verbose_name='Описание поля')

    class Meta:
        verbose_name = 'Поле документа'
        verbose_name_plural = 'Поля документа'


class Document(models.Model):
    template_id = models.ForeignKey(Template, on_delete=models.CASCADE, verbose_name='Шаблон')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор документа')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    completed = models.BooleanField(verbose_name='Документ заполнен')
    description = models.TextField(verbose_name='Описание документа')
    document_fields  = models.ManyToManyField(DocumentField, through="FieldToDocument")

    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'
        ordering = ('created',)


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
