# Generated by Django 3.2 on 2023-10-07 12:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('documents', '0002_auto_20231007_1448'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='template_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='documents.template', verbose_name='Шаблон'),
        ),
        migrations.AlterField(
            model_name='document',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Автор документа'),
        ),
        migrations.AlterField(
            model_name='documentfield',
            name='document_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='documents.document', verbose_name='Документ'),
        ),
        migrations.AlterField(
            model_name='documentfield',
            name='field_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='documents.templatefield', verbose_name='Поле'),
        ),
        migrations.AlterField(
            model_name='template',
            name='deleted',
            field=models.BooleanField(verbose_name='Удален'),
        ),
        migrations.AlterField(
            model_name='template',
            name='modified',
            field=models.DateField(verbose_name='Дата модификации'),
        ),
        migrations.AlterField(
            model_name='templatefield',
            name='template_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='documents.template', verbose_name='Шаблон'),
        ),
    ]
