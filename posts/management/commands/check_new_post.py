from datetime import datetime, timedelta

from django.core.management import BaseCommand

from posts.models.post import Post
from django.db.models import Q
from notifications.telegram.common import ADMIN_CHAT, send_telegram_message, render_html_message


class Command(BaseCommand):
    help = "Check new post"

    def handle(self, *args, **options):
#        delta = datetime.now() - timedelta(hours=18)
#        posts_query = Post.objects.filter(published_at__gte=delta, is_approved_by_moderator=True).filter(Q(type=Post.TYPE_POST) | Q(type=Post.TYPE_LINK) | Q(type=Post.TYPE_QUESTION) | Q(type=Post.TYPE_IDEA) | Q(type=Post.TYPE_PROJECT) | Q(type=Post.TYPE_EVENT) | Q(type=Post.TYPE_REFERRAL) | Q(type=Post.TYPE_BATTLE) | Q(type=Post.TYPE_GUIDE) | Q(type=Post.TYPE_THREAD))
#        if not posts_query:
#            send_telegram_message(
#                chat=ADMIN_CHAT,
#                text=render_html_message("moderator_no_new_post.html"),
#            )
        delta = datetime.now() - timedelta(hours=24)
        posts_query = Post.objects.filter(announce_at__gte=delta).exclude(announce_at__isnull=True)
        if not posts_query:
            send_telegram_message(
                chat=ADMIN_CHAT,
                text=render_html_message("moderator_no_new_announce.html"),
            )
        # delta_intro = datetime.now() - timedelta(hours=24)
        # posts_query = Post.objects.filter(created_at__gte=delta_intro).filter(type='intro')
        # if not posts_query:
        #     send_telegram_message(
        #         chat=ADMIN_CHAT,
        #         text=render_html_message("moderator_no_new_intro.html"),
        #     )
