# Generated by Django 3.2.13 on 2023-04-25 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0078_alter_affilatelogs_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='affilatelogs',
            name='percent_log',
            field=models.PositiveSmallIntegerField(default=10, null=True),
        ),
    ]
