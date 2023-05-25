# Generated by Django 3.2.13 on 2023-04-20 10:13

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0063_rename_affiliatelogs_affilatelogs'),
    ]

    operations = [
        migrations.AddField(
            model_name='affilatelogs',
            name='identify_new_user',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]
