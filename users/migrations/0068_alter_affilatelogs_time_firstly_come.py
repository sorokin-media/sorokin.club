# Generated by Django 3.2.13 on 2023-04-24 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0067_auto_20230420_1500'),
    ]

    operations = [
        migrations.AlterField(
            model_name='affilatelogs',
            name='time_firstly_come',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
