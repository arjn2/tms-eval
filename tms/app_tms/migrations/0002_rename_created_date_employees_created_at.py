# Generated by Django 4.2 on 2025-03-14 01:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_tms', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='employees',
            old_name='created_date',
            new_name='created_at',
        ),
    ]
