import json
from datetime import datetime, timedelta
from django.core.management import BaseCommand
from users.models.user import User
from notifications.email.users import payment_reminder_5_email, payment_reminder_3_email, payment_reminder_1_email
from notifications.telegram.users import payment_reminder_5, payment_reminder_3, payment_reminder_1

class Command(BaseCommand):
    help = "Fetches expiring accounts and tries to renew the subscription"

    def handle(self, *args, **options):

        expiring_users = User.objects.filter(membership_expires_at__gte=datetime.utcnow() + timedelta(days=4),
                                             membership_expires_at__lte=datetime.utcnow() + timedelta(days=5),
                                             moderation_status='approved',
                                             unitpay_id__gt=0,
                                             deleted_at__isnull=True)
        for user in expiring_users:
            self.stdout.write(f"Checking user: {user.slug}")
            self.sendMessage(user, 5)
        self.stdout.write("Done 🥙")

        expiring_users = User.objects.filter(membership_expires_at__gte=datetime.utcnow() + timedelta(days=2),
                                             membership_expires_at__lte=datetime.utcnow() + timedelta(days=3),
                                             moderation_status='approved',
                                             unitpay_id__gt=0,
                                             deleted_at__isnull=True)
        for user in expiring_users:
            self.stdout.write(f"Checking user: {user.slug}")
            self.sendMessage(user, 3)
        self.stdout.write("Done 🥙")

        expiring_users = User.objects.filter(membership_expires_at__gte=datetime.utcnow() + timedelta(days=0),
                                             membership_expires_at__lte=datetime.utcnow() + timedelta(days=1),
                                             moderation_status='approved',
                                             unitpay_id__gt=0,
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
