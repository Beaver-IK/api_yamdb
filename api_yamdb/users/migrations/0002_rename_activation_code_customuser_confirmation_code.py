# Generated by Django 3.2 on 2025-01-16 21:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='activation_code',
            new_name='confirmation_code',
        ),
    ]
