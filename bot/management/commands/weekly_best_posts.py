from django.core.management import BaseCommand

# from django.db.models import Max
# from club import settings

from posts.templatetags.text_filters import rupluralize

from posts.models.post import Post, PostExceptions
from users.models.user import User
from users.models.mute import Muted
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
import time

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
    objects_list = objects_list[:5]
    return objects_list

def construct_message(object):
    return_string = ''
    try:
        text_of_post = object.html
        text_of_post = text_of_post.replace('</a></h1>', '').replace('</a></h2>', '').replace('</a></h3>', '')
        text_of_post = text_of_post.replace('</a> </h1>', '').replace('</a> </h2>', '').replace('</a> </h3>', '')

        text_of_post = re.sub(r'\<\/[^a]\>', '', text_of_post)
        text_of_post = text_of_post.replace('&quot;', '-')

        text_of_post = re.sub(r'\<[^a/][\w\s\d\=\"\:\/\.\?\-\&\%\;]+\>|<\S>|\<\/[^a]\w+\>', '', text_of_post)
        text_of_post = re.sub(r'<h[123] id=\"\S+\"><a href=\"\#\S+\">', '', text_of_post)

        text_of_post = re.sub(r'<a href="#\S+\"\>', '', text_of_post)

        text_of_post = re.sub(r'\@[\w\d]+', '', text_of_post)

        while text_of_post[0].isspace():
            text_of_post = text_of_post[1:]

        author = object.author.full_name
        profession = object.author.position

        if object.type == 'intro':
            title_of_message = f'📝 <strong><a href="{settings.APP_HOST}/{object.type}/' \
                f'{object.slug}?utm_source=private_bot_newsletter">{author}</a></strong>\n'\
                f'       {profession}'  # spaces left on purpose, don't touch
        else:
            emoji = dict_of_emoji[object.type]
            title_of_message = f'{emoji} <strong><a href="{settings.APP_HOST}/{object.type}/' \
                f'{object.slug}?utm_source=private_bot_newsletter">{object.title}</a></strong>'

        author_link = f'<a href="{settings.APP_HOST}/user/{object.author.slug}?utm_source=private_bot_newsletter">{author}</a>'

        views = str(object.view_count) + ' 👀'
        upvotes = str(object.upvotes) + ' 👍'
        comments = str(object.comment_count) + ' 💬'
        while '\n\n' in text_of_post:
            text_of_post = text_of_post.replace('\n\n', '\n')
        while text_of_post[-1] == ' ':
            text_of_post = text_of_post[:-1]
        text_of_post = re.sub(
            r'\<img src="[\w\s\d\=\:\/\.\?\-\&\%\;]+\"{1}\salt="[\w\s\!\-\.\,\?\+\=\:\;\'\"\%\*\(\)]+\"\>', '', text_of_post)
        len_of_text = 300
        if len(text_of_post) > len_of_text:
            while len(re.findall(r'\<a', text_of_post[:len_of_text])) > len(re.findall(r'\<\/a', text_of_post[:len_of_text])):
                len_of_text += 10
            while len(re.findall(r'\<', text_of_post[:len_of_text])) > len(re.findall('\>', text_of_post[:len_of_text])):
                text_of_post = text_of_post[:-1]
            if len_of_text >= 300:
                text_of_post = text_of_post[:len_of_text] + '...'
        new_string = ''
        while 'https://sorokin' in text_of_post:
            x = re.search(r'https://sorokin[\w\s\d\=\:\/\.\?\-\&\%\;]+', text_of_post)
            start = x.start()
            finish = x.end()
            y = x.group()
            new_string = new_string + text_of_post[0:start] + y + '?utm_source=private_bot_newsletter'
            text_of_post = text_of_post[finish:]
        new_string += text_of_post

        return_string = return_string + '\n\n' + title_of_message + '\n\n' + new_string + '\n\n' + author_link + \
            ' | ' + views + ' | ' + upvotes + ' | ' + comments
    except:
        if not PostExceptions.objects.filter().exists:
            post_exception = PostExceptions()
            post_exception.post_slug = object.slug
            post_exception.foo_name = 'yesterday best posts'
            post_exception.save()
    return return_string

def compile_message_helper(bot, users_for_yesterday_digest, dict_list, header_of_message):

    COUNT_FOR_DMITRY = 0

    limit_count = 0
    start_len = len(header_of_message)
    string_for_bot = ''
    for user in users_for_yesterday_digest:
        for author_and_text in dict_list:
            author_slug = author_and_text['slug']
            # bruteforce resolvinf of problem getting value from set with one value
            for b in author_slug:
                author_slug = str(b)
            author = User.objects.get(slug=author_slug)
            is_muted = Muted.is_muted(
                user_from=user,
                user_to=author
            )
            if not is_muted:
                string_for_bot += author_and_text['text']
        if start_len != len(string_for_bot):
            string_for_bot = header_of_message + string_for_bot
            if limit_count < 50:
                time.sleep(0.100)
                limit_count += 1
                try:
                    bot.send_message(text=string_for_bot,
                                     chat_id=settings.TG_DEVELOPER_DMITRY,
                                     parse_mode=ParseMode.HTML,
                                     disable_web_page_preview=True,
                                     )
                    COUNT_FOR_DMITRY += 1
                except:
                    time.sleep(300)
                    bot.send_message(text=string_for_bot,
                                     chat_id=settings.TG_DEVELOPER_DMITRY,
                                     parse_mode=ParseMode.HTML,
                                     disable_web_page_preview=True,
                                     )
                    COUNT_FOR_DMITRY += 1
            else:
                limit_count = 0
#                time.sleep(180)
            string_for_bot = ''
    time.sleep(300)
    bot.send_message(text=f'COUNT EQUAL TO: {COUNT_FOR_DMITRY}',
                     chat_id=settings.TG_DEVELOPER_DMITRY
                     )

def send_email_helper(posts_list, intros_list, bot):

    time_zone = pytz.UTC
    now = time_zone.localize(datetime.utcnow())

    users_for_yesterday_digest = User.objects.filter(tg_weekly_best_posts=True
                                                     ).filter(membership_expires_at__gte=now
                                                              ).exclude(telegram_id=None).all()

    if posts_list:
        posts = [x['post'] for x in posts_list]
        dict_list_of_posts = []
        for object in posts:
            dict_list_of_posts.append({'text': construct_message(object), 'slug': {object.author.slug}})
            posts_string_for_bot = f'<strong>🔥 Лучшие посты клуба за прошедшую неделю 🚀</strong>'

        compile_message_helper(bot, users_for_yesterday_digest, dict_list_of_posts, posts_string_for_bot)

    if intros_list:
        intros = [x['post'] for x in intros_list]
        intros_string_for_bot = f'<strong>😺 Самые интересные интро клуба за прошедшую неделю ❤️</strong>'
        dict_list_of_intros = []
        for object in intros:
            dict_list_of_intros.append({'text': construct_message(object), 'slug': {object.author.slug}})

        compile_message_helper(bot, users_for_yesterday_digest, dict_list_of_intros, intros_string_for_bot)


class Command(BaseCommand):

    def handle(self, *args, **options):
        time_zone = pytz.UTC
        bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
        now = time_zone.localize(datetime.utcnow())
        week_ago = now - timedelta(days=7)
        week_ago_start = time_zone.localize(datetime(
            year=week_ago.year,
            month=week_ago.month,
            day=week_ago.day,
            hour=0,
            minute=0,
            second=0
        ))
        sunday = now - timedelta(days=1)
        # today is Monday by Crontab.
        week_ago_finish = time_zone.localize(datetime(
            year=sunday.year,
            month=sunday.month,
            day=sunday.day,
            hour=23,
            minute=59,
            second=59
        ))
        posts = Post.objects.filter(published_at__gte=week_ago_start
                                    ).filter(published_at__lte=week_ago_finish
                                             ).filter(is_approved_by_moderator=True
                                                      ).exclude(type='intro').all()

        intros = Post.objects.filter(published_at__gte=week_ago_start
                                     ).filter(published_at__lte=week_ago_finish
                                              ).filter(is_approved_by_moderator=True
                                                       ).filter(type='intro').all()

        posts_list = point_counter(posts)
        intros_list = point_counter(intros)

        if intros or posts:
            send_email_helper(posts_list, intros_list, bot)
