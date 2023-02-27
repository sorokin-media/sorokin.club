from datetime import datetime, timedelta

from django.core.management import BaseCommand

from posts.models.post import Post
from users.models.user import User
from notifications.telegram.users import check_user_14_days


class Command(BaseCommand):
    help = "Check intro 14 days"

    def handle(self, *args, **options):
        self.stdout.write(f"Start")
        intro_all = Post.objects.filter(published_at__gte=datetime.utcnow() + timedelta(days=14),
                                        published_at__lte=datetime.utcnow() + timedelta(days=15),
                                        type=Post.TYPE_INTRO,
                                        is_approved_by_moderator=True,
                                        deleted_at__isnull=True)
        for intro in intro_all:
            user_send = User.objects.filter(id=intro.author_id)
            self.stdout.write(f"Checking user: {user_send.slug}")
            check_user_14_days(user_send)
