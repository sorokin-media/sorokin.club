# Generated by Django 3.2.13 on 2023-12-10 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0002_coolintro_telegram_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coolintro',
            name='telegram_id',
            field=models.CharField(max_length=36, null=True, verbose_name='Telegram ID автора крутой интрухи'),
        ),
    ]
