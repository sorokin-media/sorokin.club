# Generated by Django 3.2.13 on 2023-05-25 14:48

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0005_auto_20200721_1043'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentLink',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('reference', models.CharField(db_index=True, max_length=256)),
                ('email', models.EmailField(max_length=254, null=True)),
                ('title', models.TextField()),
                ('description', models.TextField()),
                ('amount', models.IntegerField(default=0)),
                ('unitpay_id', models.CharField(max_length=128, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('started', 'started'), ('failed', 'failed'), ('success', 'success')], default='started', max_length=32)),
                ('data', models.TextField(null=True)),
            ],
            options={
                'db_table': 'payments_link',
            },
        ),
    ]
