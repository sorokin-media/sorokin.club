import base64
import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.core.management import BaseCommand
from django.template.defaultfilters import date

from club.exceptions import NotFound
from notifications.digests import generate_daily_digest
from notifications.email.sender import send_club_email
from users.models.user import User

from notifications.email.helpers import Email

log = logging.getLogger(__name__)


class Command(BaseCommand):
    ''' Django commands '''
    help = "Send daily digest"

    def add_arguments(self, parser):
        parser.add_argument("--production", type=bool, required=False, default=False)

    def handle(self, *args, **options):
        ''' to start command and get arguments if there are '''
        user = User.objects.get(slug='dev')
        try:
            digest = generate_daily_digest(user)
        except NotFound:
            self.stdout.write("Empty digest. Skipping")
            return
        digest = digest\
            .replace("%username%", user.slug)\
            .replace("%user_id%", str(user.id))\
            .replace("%secret_code%", base64.b64encode(user.secret_hash.encode("utf-8")).decode())
        # TO DO: return back previous string
        self.stdout.write("Sending email to Kir!...")

        try:
            subject = f"Дайджест за {date(datetime.utcnow(), 'd E')}"
            Email(html=digest, email='kufd.deal@gmail.com', subject=subject).send()
        except Exception as ex:
            self.stdout.write(f"Sending to Kir failed: {ex}")
            return
        self.stdout.write("Done 🥙")
