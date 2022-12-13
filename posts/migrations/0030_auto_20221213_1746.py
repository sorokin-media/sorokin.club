# Generated by Django 3.2.13 on 2022-12-13 17:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0028_auto_20221128_1307'),
        ('posts', '0029_auto_20221128_1307'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='buddy_comment_start',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='buddy_counter',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='is_waiting_buddy_comment',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='post',
            name='responsible_buddy',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='buddy', to='users.user'),
        ),
        migrations.AddField(
            model_name='post',
            name='time_task_sended',
            field=models.DateTimeField(null=True),
        ),
    ]
