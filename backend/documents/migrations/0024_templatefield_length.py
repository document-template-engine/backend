# Generated by Django 3.2 on 2023-11-03 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0023_alter_templatefieldtype_mask'),
    ]

    operations = [
        migrations.AddField(
            model_name='templatefield',
            name='length',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Размер поля ввода'),
        ),
    ]
