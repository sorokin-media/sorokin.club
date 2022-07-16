# Generated by Django 3.2.13 on 2022-07-16 05:37

from django.db import migrations, models
import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0025_add_unitpay_column'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.TextField(null=False)),
                ('default', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'subscription',
            },
        ),
        migrations.CreateModel(
            name='SubscriptionPlan',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.TextField(null=False)),
                ('amount', models.IntegerField(default=0)),
                ('description', models.TextField(null=False)),
                ('code', models.TextField(null=False)),
                ('timedelta', models.IntegerField(default=0)),
                ('package_name', models.TextField(null=False)),
                ('package_image', models.TextField(null=False)),
                ('package_price', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'subscription_plan',
            },
        ),
    ]
