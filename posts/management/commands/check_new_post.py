from datetime import datetime, timedelta

from django.core.management import BaseCommand

from posts.models.post import Post
from notifications.telegram.common import ADMIN_CHAT, send_telegram_message, render_html_message


class Command(BaseCommand):
    help = "Check new post"

    def handle(self, *args, **options):
        delta = datetime.now() - timedelta(hours=12)
        posts_query = Post.objects.filter(published_at__gte=delta).filter(type='post')
        if not posts_query:
            send_telegram_message(
                chat=ADMIN_CHAT,
                text=render_html_message("moderator_no_new_post.html"),
            )
        # delta_intro = datetime.now() - timedelta(hours=24)
        # posts_query = Post.objects.filter(created_at__gte=delta_intro).filter(type='intro')
        # if not posts_query:
        #     send_telegram_message(
        #         chat=ADMIN_CHAT,
        #         text=render_html_message("moderator_no_new_intro.html"),
        #     )
