from django.core.management import BaseCommand

#from django.db.models import Max
#from club import settings

from posts.models.post import Post
from users.models.user import User
from comments.models import Comment
#from telegramessage.models import TelegramMesage, TelegramMesageQueue
#from notifications.models import WebhookEvent

from datetime import datetime
from datetime import timedelta
import pytz

import telegram
from telegram import Update, ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext


class Command(BaseCommand):
 
    def handle(self, *args, **options):
        time_zone = pytz.UTC
        now = time_zone.localize(datetime.utcnow())
        yesterday = now - timedelta(days=1)
        yesterday_dinner = time_zone.localize(datetime(
            year=yesterday.year,
            month=yesterday.month,
            day=yesterday.day,
            hour=14,
            minute=0,
            second=0
        ))
        posts_data = []
        posts = Post.objects.filter(published_at__lte=yesterday_dinner).all()
        for post in posts:
            points = (post.upvotes*10) + (post.comment_count*3) + post.view_count
            posts_data.append({'post': post, 'points': points})
        newlist = sorted(posts_data, key=lambda post: post['points'], reverse=True)
        