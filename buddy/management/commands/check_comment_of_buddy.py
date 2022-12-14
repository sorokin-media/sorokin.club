from django.core.management import BaseCommand

from django.db.models import Max
from club import settings

from posts.models.post import Post
from users.models.user import User
from comments.models import Comment

from datetime import datetime
from datetime import timedelta
import pytz

import telegram
from telegram import Update, ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext


class Command(BaseCommand):
    '''
    Foo finds the necessary intros and sends
    messages with links to the group about such intros
    '''
    def handle(self, *args, **options):
        time_zone = pytz.UTC
        posts = Post.objects.filter(is_waiting_buddy_comment=True).all()
        if len(posts) > 0:
            for post in posts:
                time_of_buddy_start = time_zone.localize(post.buddy_comment_start)
                now = time_zone.localize(datetime.utcnow())
                delta = now - time_of_buddy_start
                if delta > timedelta(hours=3):
                    last_name = post.responsible_buddy.telegram_data['last_name']
                    first_name = post.responsible_buddy.telegram_data['first_name']
                    post.reset_buddy_status()
                    bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
                    bot.send_message(chat_id=-1001638622431,
                                     text=f'{first_name} {last_name} не задал вопрос вовремя, поэтому повторяем задачу!')
                    bot.send_message(chat_id=-1001638622431,
                                     parse_mode=ParseMode.HTML,
                                     text=f'Возращаемся к задаче! Давайте зададим вопрос пользователю. '
                                          f'<a href=\"{settings.APP_HOST}/intro/{post.slug}\">Ссылка '
                                          'на интро</a>',
                                     reply_markup=telegram.InlineKeyboardMarkup([
                                         *[
                                          [telegram.InlineKeyboardButton("Я задам! 💪",
                                           callback_data=f'buddy_get_intro {post.id}')]]]))
