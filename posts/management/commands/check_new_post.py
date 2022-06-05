from datetime import datetime, timedelta

from django.core.management import BaseCommand
from django.db import connection

from club.settings import POST_HOTNESS_PERIOD
from posts.models.post import Post
from notifications.telegram.common import ADMIN_CHAT, send_telegram_message, render_html_message, Chat


class Command(BaseCommand):
    help = "Check new post"

    def handle(self, *args, **options):
        delta = datetime.now() - timedelta(minutes=1)
        posts_query = Post.objects.filter(published_at__gte=delta).filter(type='post')
        if not posts_query:
            send_telegram_message(
                chat=ADMIN_CHAT,
                text=render_html_message("moderator_no_new_post.html"),
            )
        delta_intro = datetime.now() - timedelta(minutes=1)
        posts_query = Post.objects.filter(created_at__gte=delta).filter(type='intro')
        if not posts_query:
            send_telegram_message(
                chat=ADMIN_CHAT,
                text=render_html_message("moderator_new_post_review.html"),
            )

