# Generated by Django 3.2 on 2023-10-11 14:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0005_alter_document_completed'),
    ]

    operations = [
        migrations.RenameField(
            model_name='document',
            old_name='user_id',
            new_name='owner',
        ),
        migrations.RemoveField(
            model_name='documentfield',
            name='document_id',
        ),
        migrations.CreateModel(
            name='FieldToDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='documents.document')),
                ('fields', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='documents.documentfield')),
            ],
            options={
                'verbose_name': 'Связь между полем и документом',
                'verbose_name_plural': 'Связи между полями и документами',
            },
        ),
    ]
