# Generated by Django 3.2.13 on 2023-02-18 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0038_auto_20230218_1238'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='random_coffee_current_partner',
            field=models.CharField(db_column='random_coffee_current_partner', max_length=128, null=True),
        ),
    ]
