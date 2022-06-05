from datetime import datetime, timedelta

from django.core.management import BaseCommand

from comments.models import Comment
from notifications.telegram.common import ADMIN_CHAT, send_telegram_message


class Command(BaseCommand):
    help = "Check new comment"

    def handle(self, *args, **options):
        delta = datetime.now() - timedelta(minutes=1)
        comments_query = Comment.objects.filter(created_at__gte=delta)
        if not comments_query:
            send_telegram_message(
                chat=ADMIN_CHAT,
                text="Уже 6 часов не было ни одного нового комментария",
            )
