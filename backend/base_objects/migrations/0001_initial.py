# Generated by Django 3.2 on 2024-01-17 14:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseObject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Наименование базового обьекта')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('deleted', models.BooleanField(verbose_name='Удален')),
                ('description', models.TextField(verbose_name='Описание базового обьекта')),
            ],
            options={
                'verbose_name': 'базовый Обьекта',
                'verbose_name_plural': 'базовые Обьекты',
                'ordering': ('name',),
                'default_related_name': 'Base_objects',
            },
        ),
        migrations.CreateModel(
            name='BaseObjectField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Наименование базового поля обьекта')),
                ('base_object', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='base_fields', to='base_objects.baseobject', verbose_name='поля базового Обьект')),
            ],
            options={
                'verbose_name': 'Поле базового обьекта',
                'verbose_name_plural': 'Поля базового обьекта',
                'default_related_name': 'base_fields',
            },
        ),
        migrations.CreateModel(
            name='Object',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Наименование обьекта')),
                ('created', models.DateTimeField(auto_now=True, verbose_name='Дата создания')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('base_object', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='customer_objects', to='base_objects.baseobject', verbose_name='поля базового Обьект')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customer_objects', to=settings.AUTH_USER_MODEL, verbose_name='Автор документа')),
            ],
            options={
                'verbose_name': 'Обьект',
                'verbose_name_plural': 'Обьекты',
                'default_related_name': 'customer_objects',
            },
        ),
        migrations.CreateModel(
            name='ObjectField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(blank=True, max_length=255, null=True, verbose_name='Содержимое поля')),
                ('base_field', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='object_fields', to='base_objects.baseobjectfield', verbose_name='Поле')),
                ('object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base_objects.object', verbose_name='Обьект')),
            ],
            options={
                'verbose_name': 'Поле обьекта',
                'verbose_name_plural': 'Поля обьекта',
            },
        ),
    ]
