# Generated by Django 3.2 on 2023-10-23 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0019_auto_20231023_2010'),
    ]

    operations = [
        migrations.AlterField(
            model_name='templatefield',
            name='hint',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Подсказка'),
        ),
    ]
