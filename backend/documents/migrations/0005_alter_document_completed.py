# Generated by Django 3.2 on 2023-10-07 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0004_alter_templatefield_hint'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='completed',
            field=models.BooleanField(verbose_name='Документ заполнен'),
        ),
    ]
