import json
from datetime import datetime, timedelta
from uuid import uuid4
from django.conf import settings
from base64 import b64encode
from django.core.management import BaseCommand
from users.models.user import User
from payments.models import Payment
from notifications.email.users import send_subscribe_8_email
from notifications.email.users import couldnd_withdraw_money_email
from notifications.email.users import cancel_subscribe_user_email, payment_reminder_5_email, payment_reminder_3_email, payment_reminder_1_email
from notifications.telegram.users import subscribe_8_user
from notifications.telegram.users import couldnd_withdraw_money
from notifications.telegram.users import cancel_subscribe_user, payment_reminder_5, payment_reminder_3, payment_reminder_1, cancel_subscribe_admin
from users.models.subscription_plan import SubscriptionPlan
from payments.unitpay import UnitpayService
from urllib.request import urlopen
from urllib.parse import quote
from notifications.telegram.common import Chat, send_telegram_message, ADMIN_CHAT, render_html_message
from django.urls import reverse


class Command(BaseCommand):
    help = "Fetches expiring accounts and tries to renew the subscription"

    def handle(self, *args, **options):

        expiring_users = User.objects.filter(membership_expires_at__gte=datetime.utcnow() + timedelta(days=4),
                                             membership_expires_at__lte=datetime.utcnow() + timedelta(days=5),
                                             moderation_status='approved',
                                             deleted_at__isnull=True)
        for user in expiring_users:
            self.stdout.write(f"Checking user: {user.slug}")
            self.sendMessage(user, 5)
        self.stdout.write("Done 🥙")

        expiring_users = User.objects.filter(membership_expires_at__gte=datetime.utcnow() + timedelta(days=2),
                                             membership_expires_at__lte=datetime.utcnow() + timedelta(days=3),
                                             moderation_status='approved',
                                             deleted_at__isnull=True)
        for user in expiring_users:
            self.stdout.write(f"Checking user: {user.slug}")
            self.sendMessage(user, 3)
        self.stdout.write("Done 🥙")

        expiring_users = User.objects.filter(membership_expires_at__gte=datetime.utcnow() + timedelta(days=0),
                                             membership_expires_at__lte=datetime.utcnow() + timedelta(days=1),
                                             moderation_status='approved',
                                             deleted_at__isnull=True)
        for user in expiring_users:
            self.stdout.write(f"Checking user: {user.slug}")
            self.sendMessage(user, 1)
        self.stdout.write("Done 🥙")

    def sendMessage(self, user, daysNum):
        if user.unitpay_id > 0:
            self.stdout.write("Done 🥙")
        else:
            if daysNum == 5:
                payment_reminder_5_email(user)
                payment_reminder_5(user)
            if daysNum == 3:
                payment_reminder_3_email(user)
                payment_reminder_3(user)
            if daysNum == 1:
                payment_reminder_1_email(user)
                payment_reminder_1(user)
