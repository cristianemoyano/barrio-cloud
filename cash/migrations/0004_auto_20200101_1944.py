# Generated by Django 2.2.9 on 2020-01-01 19:44

from django.db import migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('cash', '0003_auto_20200101_1943'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='notes',
            field=tinymce.models.HTMLField(blank=True, null=True),
        ),
    ]
