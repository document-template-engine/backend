# Generated by Django 3.2 on 2023-10-25 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0022_auto_20231025_2055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='templatefieldtype',
            name='mask',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Маска допустимых значений'),
            preserve_default=False,
        ),
    ]