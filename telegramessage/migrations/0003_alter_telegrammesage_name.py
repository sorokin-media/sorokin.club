# Generated by Django 3.2.13 on 2023-01-13 21:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telegramessage', '0002_auto_20230113_2056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telegrammesage',
            name='name',
            field=models.CharField(max_length=256, unique=True),
        ),
    ]
