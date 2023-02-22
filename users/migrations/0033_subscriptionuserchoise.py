# Generated by Django 3.2.13 on 2023-02-13 10:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0032_delete_subscriptionuserchoise'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscriptionUserChoise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('daily_email_digest', models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False, verbose_name='Ежедневная e-mail рассылка')),
                ('weekly_email_digest', models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False, verbose_name='Еженедельная e-mail рассылка')),
                ('tg_yesterday_best_posts', models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False, verbose_name='Лучшие посты и самые интересные интро за вчерашний день')),
                ('tg_weekly_best_posts', models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False, verbose_name='Лучшие посты и интересные интро за прошедшую неделю')),
                ('user_id', models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, related_name='subscription_user_choises', to='users.user')),
            ],
            options={
                'db_table': 'subscription_user_choises',
            },
        ),
    ]
