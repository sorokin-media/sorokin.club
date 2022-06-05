from datetime import datetime, timedelta

from django.core.management import BaseCommand
from django.db import connection

from comments.models import Comment
from notifications.telegram.common import ADMIN_CHAT, send_telegram_message, render_html_message, Chat


class Command(BaseCommand):
    help = "Check new comment"

    def handle(self, *args, **options):
        delta = datetime.now() - timedelta(hours=6)
        comments_query = Comment.objects.filter(created_at__gte=delta)
        if not comments_query:
            send_telegram_message(
                chat=ADMIN_CHAT,
                text=render_html_message("moderator_no_new_post.html"),
            )

