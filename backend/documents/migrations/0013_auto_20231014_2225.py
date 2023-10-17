# Generated by Django 3.2 on 2023-10-14 19:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0012_auto_20231014_2014'),
    ]

    operations = [
        migrations.RenameField(
            model_name='templatefield',
            old_name='template_id',
            new_name='template',
        ),
        migrations.CreateModel(
            name='TemplateFieldGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Наименование группы полей')),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='field_groups', to='documents.template', verbose_name='Шаблон')),
            ],
            options={
                'verbose_name': 'Группа полей',
                'verbose_name_plural': 'Группы полей',
                'ordering': ('id',),
            },
        ),
        migrations.AddField(
            model_name='templatefield',
            name='group',
            field=models.ForeignKey(blank=True, help_text='Группа полей в шаблоне', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fields', to='documents.templatefieldgroup', verbose_name='Группа'),
        ),
    ]
