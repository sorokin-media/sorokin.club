import base64
import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.core.management import BaseCommand
from django.template.defaultfilters import date

from club.exceptions import NotFound
from notifications.digests import generate_daily_digest
from notifications.email.sender import Email

from users.models.user import User


log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Send daily digest"

    def add_arguments(self, parser):
        parser.add_argument("--production", type=bool, required=False, default=False)


# 
    def handle(self, *args, **options):
        # select daily subscribers
        subscribed_users = User.objects\
            .filter(
                daily_email_digest=True,
                is_email_verified=True,
                membership_expires_at__gte=datetime.utcnow(),
                moderation_status=User.MODERATION_STATUS_APPROVED,
            )\
            .exclude(is_email_unsubscribed=True)
        self.stdout.write(f'{subscribed_users}')
        # TO FIX: class EMAIL use API that can get list of emails. 
        # So, it's better to send one time to list either 
        # one time to one user
        for user in subscribed_users:
            if not options.get("production") and user.email not in dict(settings.ADMINS).values():
                self.stdout.write("Test mode. Use --production to send the digest to all users")
                continue
            # render user digest using a special html endpoint
            try:
                digest = generate_daily_digest(user)
            except NotFound:
                continue
            digest = digest\
                .replace("%username%", user.slug)\
                .replace("%user_id%", str(user.id))\
                .replace("%secret_code%", base64.b64encode(user.secret_hash.encode("utf-8")).decode())
            self.stdout.write(f"Sending email to {user.email}...")
            try:
                email = Email(
                    html=digest,
                    email=user.email,
                    subject=f"Дайджест за {date(datetime.utcnow(), 'd E')}"
                )
                email.prepare_email()
                email.send()
            except Exception as ex:
                self.stdout.write(f"Sending to {user.email} failed: {ex}")
        self.stdout.write("Done 🥙")


# previouse version of sending message, befor using UNISENDER API
#
#
#                send_club_email(
#                    recipient=user.email,
#                    subject=f"Дайджест за {date(datetime.utcnow(), 'd E')}",
#                    html=digest,
#                    tags=["daily_digest"]
#                )
