# Generated by Django 3.2.13 on 2023-07-04 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0005_alter_apps_jwt_secret'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='original_token',
            field=models.CharField(max_length=127, null=True, unique=True),
        ),
    ]
