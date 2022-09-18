from datetime import datetime, timedelta

from django.core.management import BaseCommand

from posts.models.post import Post
from badges.models import Badge, UserBadge
from users.models.user import User
from django.conf import settings
from django.db.models import Q


class Command(BaseCommand):
    help = "Check new post"

    def handle(self, *args, **options):
        posts_query = Post.objects.filter(created_at__gte=datetime(2022, 9, 18),
                                             upvotes__gt=settings.ADD_DOLOR_POST_UPVOTE,
                                             type='post',
                                             upvote_badge=False).filter(Q(type=Post.TYPE_POST) | Q(type=Post.TYPE_LINK) | Q(type=Post.TYPE_QUESTION) | Q(type=Post.TYPE_IDEA) | Q(type=Post.TYPE_PROJECT) | Q(type=Post.TYPE_EVENT) | Q(type=Post.TYPE_REFERRAL) | Q(type=Post.TYPE_BATTLE) | Q(type=Post.TYPE_GUIDE) | Q(type=Post.TYPE_THREAD))
        for post_one in posts_query:
            print(post_one)
            admin = User.objects.filter(id='e97c6342-7bb7-4b2d-bb23-bdd147de14db').first()
            badge = Badge.objects.filter(code='dolor').first()
            user_badge = UserBadge.create_user_badge_post_admin(
                badge=badge,
                from_user=admin,
                to_user=post_one.author,
                post=post_one
            )

