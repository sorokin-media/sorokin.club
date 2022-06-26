import logging
import json
from datetime import datetime, timedelta

from django.core.management import BaseCommand
from users.models.user import User
from payments.models import Payment
from notifications.email.users import send_subscribe_8_email
from notifications.telegram.users import subscribe_8_user


class Command(BaseCommand):
    help = "Fetches expiring accounts and tries to renew the subscription"

    def handle(self, *args, **options):

        expiring_users = User.objects.filter(membership_expires_at__gte=datetime.utcnow() + timedelta(days=8),membership_expires_at__lte=datetime.utcnow() + timedelta(days=9),unitpay_id__isnull=False)

        for user in expiring_users:
            self.stdout.write(f"Checking user: {user.slug}")
            payment_last = Payment.objects.filter(user_id=user.id,status='success').last()
            payment_json = json.loads(payment_last.data)
            send_subscribe_8_email(user, payment_last.amount, payment_json['params[purse]'])
            subscribe_8_user(user, payment_last.amount, payment_json['params[purse]'])
        self.stdout.write("Done 🥙")
