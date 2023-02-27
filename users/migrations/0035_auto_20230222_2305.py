# Generated by Django 3.2.13 on 2023-02-22 23:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0034_auto_20230222_1012'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='daily_email_digest',
            field=models.BooleanField(default=False, null=True, verbose_name='Ежедневная e-mail рассылка'),
        ),
        migrations.AlterField(
            model_name='user',
            name='tg_weekly_best_posts',
            field=models.BooleanField(default=False, null=True, verbose_name='Лучшие посты и интересные интро за прошедшую неделю'),
        ),
        migrations.AlterField(
            model_name='user',
            name='tg_yesterday_best_posts',
            field=models.BooleanField(default=False, null=True, verbose_name='Лучшие посты и самые интересные интро за вчерашний день'),
        ),
    ]
