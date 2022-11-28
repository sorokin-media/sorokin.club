# Generated by Django 3.2.13 on 2022-11-28 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0027_auto_20220716_0603'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='membership_platform_type',
            field=models.CharField(choices=[('direct', 'Direct'), ('patreon', 'Patreon'), ('crypto', 'Crypto')], default='patreon', max_length=128),
        ),
        migrations.AlterField(
            model_name='user',
            name='unitpay_id',
            field=models.IntegerField(default=0),
        ),
    ]
