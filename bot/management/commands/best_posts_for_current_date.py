# Django core and Django ORM imports
from django.core.management import BaseCommand
from django.db.models import Q

# imports for getting config data
from club import settings

# import for working with words in Russian (singular, plural)
from posts.templatetags.text_filters import rupluralize

# import Models
from posts.models.post import Post, PostExceptions
from users.models.user import User
from users.models.mute import Muted

# time imports
from datetime import datetime
from datetime import timedelta
import pytz

# Telegram imports
import telegram
from telegram import Update, ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

# import Python packages
import re

# import custom class for sending message in Telegram
from bot.sending_message import TelegramCustomMessage

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
    '''foo counting points for determing best posts and intros '''
    objects_data = []
    for object in objects:
        points = (object.upvotes*10) + (object.comment_count*3) + object.view_count
        objects_data.append({'post': object, 'points': points})
    objects_list = sorted(objects_data, key=lambda post: post['points'], reverse=True)
    objects_list = objects_list[:3]
    return objects_list


def construct_message(object):
    '''foo formates text for message from html type '''
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
        company = object.author.company

        if object.type == 'intro':
            title_of_message = f'📝 <strong><a href="{settings.APP_HOST}/{object.type}/' \
                f'{object.slug}?utm_source=private_bot_newsletter">{author}</a></strong>\n'\
                f'{profession} - {company}'  # spaces left on purpose, don't touch
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
            # quick fix bug with post https://sorokin.club/event/1330/
            while len(re.findall(r'\<a', text_of_post[:len_of_text])) > len(re.findall('\<\/a', text_of_post[:len_of_text])):
                text_of_post = text_of_post[:-1]
            if text_of_post[-1] == '<':
                text_of_post = text_of_post[:-1]
            # enf of fix
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
    ''' foo send messages to user'''
    start_len = len(header_of_message)
    string_for_bot = ''

    post_photo = 'https://sorokin.club/static/images/best_posts_day.png'
    intro_photo = 'https://sorokin.club/static/images/intro_day.png'

    for user in users_for_yesterday_digest:
        for author_and_text in dict_list:
            author_slug = author_and_text['slug']
            # bruteforce resolving of problem getting value from set with one value
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
            # quick ifx of bug, it's better to check out
            if user.slug not in ['AlekseiPodkletnov', 'den-is', 'Lisa', 'nabiullin', 'hichnii', 'rav'] and user.slug not in ['vika', 'skorpion28', 'sesevor']:
                if 'посты' in header_of_message:
                    custom_message = TelegramCustomMessage(
                        etc=author,
                        user=user,
                        string_for_bot='',
                        photo=post_photo
                    )
                    custom_message.send_photo()
                    custom_message = TelegramCustomMessage(
                        etc=author,
                        user=user,
                        string_for_bot=string_for_bot
                    )
                    string_for_bot = ''
                    custom_message.send_message()
                elif 'интро' in header_of_message:
                    custom_message = TelegramCustomMessage(
                        etc=author,
                        user=user,
                        string_for_bot='',
                        photo=intro_photo
                    )
                    custom_message.send_photo()
                    custom_message = TelegramCustomMessage(
                        etc=author,
                        user=user,
                        string_for_bot=string_for_bot
                    )
                    string_for_bot = ''
                    custom_message.send_message()
        string_for_bot = ''
    custom_message.send_count_to_dmitry(type_='Рассылка постов и интро')


def send_email_helper(posts_list, intros_list, bot, date_day, date_month):
    ''' foo creates users list and basic text of message like Title, etc'''

    time_zone = pytz.UTC
    now = time_zone.localize(datetime.utcnow())
    date_month = dict_of_year[date_month]
#    users_for_yesterday_digest = User.objects.filter(tg_yesterday_best_posts=True
#                                                     ).filter(membership_expires_at__gte=now
#                                                              ).exclude(telegram_id=None
#                                                                        ).exclude(telegram_id='').all()
#    users_for_yesterday_digest = User.objects.get(slug='romashovdmitryo')
    # for test on local
    users_for_yesterday_digest = [
        User.objects.get(slug='romashovdmitryo'), 
        User.objects.get(slug='Anna_Golubova')
    ]
    if posts_list:
        posts = [x['post'] for x in posts_list]
        dict_list_of_posts = []
        for object in posts:
            dict_list_of_posts.append({'text': construct_message(object), 'slug': {object.author.slug}})
        posts_string_for_bot = f'Упс! Произошла техническая накладка. Рассылка долетела не всем. '\
            f'Приносим извинения и делимся лучшими постами за 26-ое число!'\
            f'\n\n<strong>🔥 Лучшие посты клуба за {date_day} {date_month} 🚀</strong>'

        compile_message_helper(bot, users_for_yesterday_digest, dict_list_of_posts, posts_string_for_bot)

    if len(intros_list) > 0:
        intros = [x['post'] for x in intros_list]
        intros_string_for_bot = f'Упс! Произошла техническая накладка. Рассылка долетела не всем. '\
            f'Приносим извинения и делимся лучшими интро за 26-ое число!'\
            f'<strong>😺 Самые интересные интро {date_day} {date_month} ❤️</strong>'
        dict_list_of_intros = []
        for object in intros:
            dict_list_of_intros.append({'text': construct_message(object), 'slug': {object.author.slug}})

        compile_message_helper(bot, users_for_yesterday_digest, dict_list_of_intros, intros_string_for_bot)

class Command(BaseCommand):
    '''Foo creates list if best posts '''

    def handle(self, *args, **options):

        time_zone = pytz.UTC
        bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
        now = time_zone.localize(datetime.utcnow())
        date_start = time_zone.localize(datetime(
            year=2023,
            month=6,
            day=26,
            hour=0,
            minute=0,
            second=0
        ))
        date_finish = time_zone.localize(datetime(
            year=2023,
            month=6,
            day=26,
            hour=23,
            minute=59,
            second=59
        ))
        posts = Post.objects.filter(published_at__gte=date_start
                                    ).filter(published_at__lte=date_finish
                                             ).filter(is_approved_by_moderator=True
                                                      ).exclude(type='intro'
                                                                ).filter(author__in=User.objects.filter(Q(is_banned_until__lte=now) | Q(is_banned_until=None)).all()
                                                                         ).all()

        intros = Post.objects.filter(published_at__gte=date_start
                                     ).filter(published_at__lte=date_finish
                                              ).filter(is_approved_by_moderator=True
                                                       ).filter(type='intro'
                                                                ).filter(author__in=User.objects.filter(Q(is_banned_until__lte=now) | Q(is_banned_until=None)).all()
                                                                         ).all()

        posts_list = point_counter(posts)
        intros_list = point_counter(intros)
        if intros or posts:
            date_day = date_start.day
            day_month = date_start.month
            send_email_helper(posts_list, intros_list, bot, date_day, day_month)
