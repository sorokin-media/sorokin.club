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
from users.models.subscription import SubscriptionUserChoise

import telegram
from telegram import Update, ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

import re

dict_of_year = {1: 'января',
                2: 'февраля',
                3: 'марта',
                4: 'апреля',
                5: 'мая',
                6: 'июня',
                7: 'июля',
                8: 'августа',
                9: 'сентября',
                10: 'октября',
                11: 'ноября',
                12: 'декабря'}

dict_of_emoji = {
    'post': '📝',
    'event': '📅',
    'link': '🔗',
    'question': '🤔',
    'idea': '💡',
    'thread': '🗄️'
}

def point_counter(objects):
    objects_data = []
    for object in objects:
        points = (object.upvotes*10) + (object.comment_count*3) + object.view_count
        objects_data.append({'post': object, 'points': points})
    objects_list = sorted(objects_data, key=lambda post: post['points'], reverse=True)
    objects_list = objects_list[:3]
    return objects_list

def construct_message(objects):
    return_string = ''
    for object in objects:
        text_of_post = object.text
        text_of_post = text_of_post[:250] + '...'
        text_of_post = re.sub(r'\!\[\]\(https\S+', '', text_of_post)
        text_of_post = re.sub(r'\[\]\(https\S+', '', text_of_post)
        if '](https' in text_of_post:
            new_string = ''
            how_much = re.findall(r']\(http\S+', text_of_post)
            for _ in range(len(how_much)):
                link = re.search(r']\(http\S+', text_of_post)
                text = re.search(r'\[[\D|\s|]+]', text_of_post)
                start = text.start()
                finish = link.end()
                link = link.group()
                link = link[2:-1]
                print(f'LINK:{link}')
                formating_text = f'<strong><a href="{link}?utm_source=private_bot_newsletter">{text.group()}</a></strong>'
                new_string = new_string + text_of_post[:start] + formating_text
                text_of_post = text_of_post[finish:]
            text_of_post = new_string + text_of_post
        text_of_post = re.sub(r' @\S+ ', '', text_of_post)
        text_of_post = re.sub(r'@\S+ ', '', text_of_post)
        text_of_post = text_of_post.replace('![](', '')
        text_of_post = text_of_post.replace("*", "")
        text_of_post = text_of_post.replace("```", "")
        text_of_post = text_of_post.replace("#", "")

        author = object.author.full_name

        if object.type == 'intro':
            title_of_message = f'📝 <strong><a href="{settings.APP_HOST}/{object.type}/' \
                f'{object.slug}?utm_source=private_bot_newsletter">{author}</a></strong>'
        else:
            emoji = dict_of_emoji[object.type]
            title_of_message = f'{emoji} <strong><a href="{settings.APP_HOST}/{object.type}/' \
                f'{object.slug}?utm_source=private_bot_newsletter">{object.title}</a></strong>'

        author_link = f'<a href="{settings.APP_HOST}/user/{object.author.slug}?utm_source=private_bot_newsletter">{author}</a>'

        views = str(object.view_count) + ' 👀'
        if object.upvote_badge is not False:
            upvotes = str(object.upvote_badge) + ' 👍'
        else:
            upvotes = '0 👍'
        comments = str(object.comment_count) + ' 💬'
        return_string = return_string + '\n\n' + title_of_message + '\n\n' + text_of_post + '\n\n' + author_link + \
            ' | ' + views + ' | ' + upvotes + ' | ' + comments
    return return_string

def send_email_helper(posts_list, intros_list, bot, date_day, date_month):

    users_for_yesterday_digest = SubscriptionUserChoise.objects.filter(tg_yesterday_best_posts=True).values("user_id")
    telegram_ids = []
    for user_id in users_for_yesterday_digest:
        telegram_id = User.objects.filter(id=user_id['user_id']).first().telegram_id
        telegram_ids.append(telegram_id)

    date_month = dict_of_year[date_month]

    if len(telegram_ids) > 0:

        if posts_list:
            posts = [x['post'] for x in posts_list]
            posts_string_for_bot = f'<strong>🔥 Лучшие посты клуба за {date_day} {date_month} 🚀</strong>'
            posts_string_for_bot = posts_string_for_bot + construct_message(posts)
            for _ in telegram_ids:
                bot.send_message(text=posts_string_for_bot,
                                 chat_id=_,
                                 parse_mode=ParseMode.HTML,
                                 disable_web_page_preview=True,
                                 )

        if intros_list:
            intros = [x['post'] for x in intros_list]
            intros_string_for_bot = f'<strong>😺 Самые интересные интро {date_day} {date_month} ❤️</strong>'
            intros_string_for_bot = intros_string_for_bot + construct_message(intros, date_month, date_day)
            for _ in telegram_ids:
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
        yesterday_start = time_zone.localize(datetime(
            year=yesterday.year,
            month=yesterday.month,
            day=yesterday.day,
            hour=0,
            minute=0,
            second=0
        ))
        yesterday_finish = time_zone.localize(datetime(
            year=yesterday.year,
            month=yesterday.month,
            day=yesterday.day,
            hour=23,
            minute=59,
            second=59
        ))
        posts = Post.objects.filter(published_at__gte=yesterday_start
                                    ).filter(published_at__lte=yesterday_finish
                                             ).filter(is_approved_by_moderator=True
                                                      ).exclude(type='intro').all()

        intros = Post.objects.filter(published_at__gte=yesterday_start
                                     ).filter(published_at__lte=yesterday_finish
                                              ).filter(is_approved_by_moderator=True
                                                       ).filter(type='intro').all()

        posts_list = point_counter(posts)
        intros_list = point_counter(intros)

        if intros or posts:
            date_day = yesterday_start.day
            day_month = yesterday_start.month
            send_email_helper(posts_list, intros_list, bot, date_day, day_month)
