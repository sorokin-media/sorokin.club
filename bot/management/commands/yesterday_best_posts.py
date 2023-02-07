from django.core.management import BaseCommand

# from django.db.models import Max
# from club import settings

from posts.templatetags.text_filters import rupluralize

from posts.models.post import Post
from users.models.user import User
from comments.models import Comment

from datetime import datetime
from datetime import timedelta
import pytz

from django.template import loader

from notifications.email.sender import send_club_email
from django.dispatch import receiver

from club import settings
from users.models.user import User

import telegram
from telegram import Update, ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

import re

dict_of_year = {1: 'Января',
                2: 'Февраля',
                3: 'Марта',
                4: 'Апреля',
                5: 'Мая',
                6: 'Июня',
                7: 'Июля',
                8: 'Августа',
                9: 'Сентября',
                10: 'Октября',
                11: 'Ноября',
                12: 'Декабря'}

def point_counter(objects):
    objects_data = []
    for object in objects:
        points = (object.upvotes*10) + (object.comment_count*3) + object.view_count
        objects_data.append({'post': object, 'points': points})
    objects_list = sorted(objects_data, key=lambda post: post['points'], reverse=True)
    objects_list = objects_list[:3]
    return objects_list

def construct_message(objects, date_month, date_day):
    return_string = ''
    for object in objects:
        title_of_message = f'<strong><a href="{settings.APP_HOST}/post/{object.slug}">{object.title}</a></strong>'
        text_of_post = object.text[:250] + '...'
        text_of_post = re.sub(r'http\S+', '', text_of_post)
        text_of_post = text_of_post.replace('![](', '')
        author = object.author.full_name
        author_link = f'<a href="{settings.APP_HOST}/user/{object.author.slug}">{author}</a>'

        views = str(object.view_count) + rupluralize(value=object.view_count, arg='просмотр, просмотры, просмотров')
        if object.upvote_badge is not False:
            upvotes = str(object.upvote_badge) + rupluralize(value=object.upvote_badge, arg='плюс, плюсы, плюсов')
        else:
            upvotes = '0 плюсов'
        comments = str(object.comment_count) + rupluralize(value=object.comment_count,
                                                           arg='комментарий, коментарии, комментариев')
        return_string = return_string + '\n\n' + title_of_message + '\n\n' + text_of_post + '\n\n' + author_link + \
            ' | ' + views + ' | ' + upvotes + ' | ' + comments
    return return_string

def send_email_helper(posts_list, intros_list, bot, date_day, date_month):
    me = User.objects.filter(slug='romashovdmitryo').first().telegram_id
    alex = User.objects.filter(slug='bigsmart').first().telegram_id
    me_and_alex = [me, alex]
    date_month = dict_of_year[date_month]

    if posts_list:
        posts = [x['post'] for x in posts_list]
        posts_string_for_bot = f'<strong>🤟 Лучшие посты за {date_day} {date_month} 😎</strong>'
        posts_string_for_bot = posts_string_for_bot + construct_message(posts, date_month, date_day)
        for _ in me_and_alex:
            bot.send_message(text=posts_string_for_bot,
                             chat_id=_,
                             parse_mode=ParseMode.HTML,
                             disable_web_page_preview=True
                             )

    if intros_list:
        intros = [x['post'] for x in intros_list]
        intros_string_for_bot = f'<strong>👩‍🎓 Самые интересные интро {date_day} {date_month} 🧑‍🎓</strong>'
        intros_string_for_bot = intros_string_for_bot + construct_message(intros, date_month, date_day)
        for _ in me_and_alex:
            bot.send_message(text=intros_string_for_bot,
                             chat_id=_,
                             parse_mode=ParseMode.HTML,
                             disable_web_page_preview=True
                             )

class Command(BaseCommand):

    def handle(self, *args, **options):
        time_zone = pytz.UTC
        bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
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
        yesterday_start = yesterday_dinner - timedelta(days=1)

        posts = Post.objects.filter(published_at__gte=yesterday_start
                                    ).filter(published_at__lte=yesterday_dinner
                                             ).filter(is_approved_by_moderator=True
                                                      ).filter(type='post').all()

        intros = Post.objects.filter(published_at__gte=yesterday_start
                                     ).filter(published_at__lte=yesterday_dinner
                                              ).filter(is_approved_by_moderator=True
                                                       ).filter(type='intro').all()

        posts_list = point_counter(posts)
        intros_list = point_counter(intros)

        if intros or posts:
            date_day = yesterday_start.day
            day_month = yesterday_start.month
            send_email_helper(posts_list, intros_list, bot, date_day, day_month)
