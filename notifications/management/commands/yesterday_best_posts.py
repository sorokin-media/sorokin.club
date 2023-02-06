from django.core.management import BaseCommand

# from django.db.models import Max
# from club import settings

from posts.models.post import Post
from users.models.user import User
from comments.models import Comment
# from telegramessage.models import TelegramMesage, TelegramMesageQueue
# from notifications.models import WebhookEvent

from datetime import datetime
from datetime import timedelta
import pytz

from django.template import loader

from notifications.email.sender import send_club_email
from django.dispatch import receiver

'''
DON'T FORGET UNCOMMENT SETTING.PY ABOUT EMAIL

'''

def send_email_helper(posts_list, intros_list):
    posts = [x['post'] for x in posts_list]
    intros = [x['intro'] for x in intros_list]
    renewal_template = loader.get_template("emails/everyday_best_posts.html")

    test_users = ['romashov.dmitry.o@gmail.com', 'bigsmart@gmail.com']

    for user in test_users:
        send_club_email(recipient=user,
                        subject=f"Лучшие интро и новички прошедшой недели.",
                        html=renewal_template.render({'intros': intros,
                                                      'posts': posts}),
                        tags=["comment"])


    # можно передавать аргументы в render() в виде ключ + значение
'''
DON'T FORGET UNCOMMENT SETTING.PY ABOUT EMAIL

'''


class Command(BaseCommand):

    def handle(self, *args, **options):
        time_zone = pytz.UTC
        # настоящий момент, 14:00
        now = time_zone.localize(datetime.utcnow())
        # вчерашний день в целом
        yesterday = now - timedelta(days=1)
        # вчерашний обед
        yesterday_dinner = time_zone.localize(datetime(
            year=yesterday.year,
            month=yesterday.month,
            day=yesterday.day,
            hour=14,
            minute=0,
            second=0
        ))
        yesterday_start = yesterday_dinner - timedelta(days=30)
# для теста пока оставляю
#        yesterday_dinner = time_zone.localize(datetime.utcnow())
# для теста оставляю пока что
#        yesterday_start = yesterday_dinner - timedelta(days=100)
        posts_data = []
        intros_data = []
        posts = Post.objects.filter(published_at__gte=yesterday_start
                                    ).filter(published_at__lte=yesterday_dinner
                                             ).filter(is_approved_by_moderator=True
                                                      ).filter(type='post').all()

        intros = Post.objects.filter(published_at__gte=yesterday_start
                                     ).filter(published_at__lte=yesterday_dinner
                                              ).filter(is_approved_by_moderator=True
                                                       ).filter(type='intro').all()

        for post in posts:
            points = (post.upvotes*10) + (post.comment_count*3) + post.view_count
            posts_data.append({'post': post, 'points': points})
        posts_list = sorted(posts_data, key=lambda post: post['points'], reverse=True)
        posts_list = posts_list[:3]

        for intro in intros:
            points = (intro.upvotes*10) + (intro.comment_count*3) + intro.view_count
            intros_data.append({'intro': intro, 'points': points})
        intros_list = sorted(intros_data, key=lambda intro: intro['points'], reverse=True)
        intros_list = intros_list[:3]

#   берём только посты пока

        if intros or posts:
            send_email_helper(posts_list, intros_list)
