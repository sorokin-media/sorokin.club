import json
from datetime import datetime, timedelta
from django.core.management import BaseCommand
from users.models.user import User
from notifications.telegram.users import cancel_subscribe_admin, send_telegram_message, Chat


class Command(BaseCommand):
    help = "Fetches expiring accounts and tries to renew the subscription"

    def handle(self, *args, **options):
        expiring_users = User.objects.filter(membership_expires_at__gte=datetime.utcnow() + timedelta(seconds=-330),
                                             membership_expires_at__lte=datetime.utcnow(),
                                             moderation_status='approved',
                                             deleted_at__isnull=True)
        for user in expiring_users:
            self.stdout.write(f"Checking user: {user.slug}")
            send_telegram_message(
                chat=Chat(id=204349098),
                text=f"Test 123 123 123 123",
            )
            self.cancelSubUser(user)
        self.stdout.write("Done 🥙")

    def cancelSubUser(self, user):
        cancel_subscribe_admin(user)
