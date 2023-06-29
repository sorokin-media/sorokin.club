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
from bot.sending_message import TelegramCustomMessage, MessageToDmitry

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
    objects_list = objects_list[:5]
    return objects_list

def construct_message(object, custom_utm=None):
    '''foo formates text for message from html type '''

    return_string = ''
    try:
        text_of_post = object.html
        # clean html tags first block
        text_of_post = text_of_post.replace('</a></h1>', '').replace('</a></h2>', '').replace('</a></h3>', '')
        text_of_post = text_of_post.replace('</a> </h1>', '').replace('</a> </h2>', '').replace('</a> </h3>', '')

        text_of_post = re.sub(r'\<\/[^a]\>', '', text_of_post)
        text_of_post = text_of_post.replace('&quot;', '-')
        # clean html tags second block
        text_of_post = re.sub(r'\<[^a/][\w\s\d\=\"\:\/\.\?\-\&\%\;]+\>|<\S>|\<\/[^a]\w+\>', '', text_of_post)
        text_of_post = re.sub(r'<h[123] id=\"\S+\"><a href=\"\#\S+\">', '', text_of_post)
        # clean all a href
        text_of_post = re.sub(r'<a href="#\S+\"\>', '', text_of_post)
        # clean all mention of users
        text_of_post = re.sub(r'\@[\w\d]+', '', text_of_post)
        # clean first symbol if it is space
        while text_of_post[0].isspace():
            text_of_post = text_of_post[1:]

        author = object.author.full_name
        profession = object.author.position
        company = object.author.company

        # start working on UTM
        if object.type == 'intro':
            if custom_utm:
                title_of_message = f'📝 <strong><a href="{settings.APP_HOST}/{object.type}/' \
                    f'{object.slug}?{custom_utm}">{author}</a></strong>\n'\
                    f'{profession} - {company}'
            else:
                title_of_message = f'📝 <strong><a href="{settings.APP_HOST}/{object.type}/' \
                    f'{object.slug}?utm_source=private_bot_newsletter">{author}</a></strong>\n'\
                    f'{profession} - {company}'
        else:
            emoji = dict_of_emoji[object.type]
            if custom_utm:
                title_of_message = f'{emoji} <strong><a href="{settings.APP_HOST}/{object.type}/' \
                    f'{object.slug}?{custom_utm}">{object.title}</a></strong>'
            else:
                title_of_message = f'{emoji} <strong><a href="{settings.APP_HOST}/{object.type}/' \
                    f'{object.slug}?utm_source=private_bot_newsletter">{object.title}</a></strong>'
        if custom_utm:
            author_link = f'<a href="{settings.APP_HOST}/user/{object.author.slug}?{custom_utm}">{author}</a>'
        else:
            author_link = f'<a href="{settings.APP_HOST}/user/{object.author.slug}?utm_source=private_bot_newsletter">{author}</a>'
        # finish working on UTM

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
            # add UTM to every link
            if custom_utm:
                new_string = new_string + text_of_post[0:start] + y + '?' + custom_utm
            else:
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


'''

    For tests on prod.

    user_1 = User.objects.get(slug='romashovdmitryo')
    user_2 = User.objects.get(slug='Anna_Golubova')

    my_users = []

    my_users.append(user_1)
    my_users.append(user_2)

    and also to add for test -> 
    if user in my_users: 

'''

def compile_message_helper(bot, users_for_weekly_digest, dict_list, header_of_message, optional=None):
    ''' foo send messages to user'''
    start_len = len(header_of_message)
    string_for_bot = ''
    post_photo = 'https://sorokin.club/static/images/open_posts_weekly.png'
    closed_post_photo = 'https://sorokin.club/static/images/closed_posts_weekly.png'
    intro_photo = 'https://sorokin.club/static/images/weekly_intros.png'
    for user in users_for_weekly_digest:
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
            if optional:
                string_for_bot = header_of_message + string_for_bot + optional
            else:
                string_for_bot = header_of_message + string_for_bot
            if user.slug not in ['AlekseiPodkletnov', 'den-is', 'Lisa', 'nabiullin', 'hichnii', 'rav'] and user.slug not in ['vika', 'skorpion28', 'sesevor']:
                if 'лучшие посты' in header_of_message:
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
                elif 'лучшие открытые посты' in header_of_message:
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
                elif 'лучшие закрытые посты' in header_of_message:
                    custom_message = TelegramCustomMessage(
                        etc=author,
                        user=user,
                        string_for_bot='',
                        photo=closed_post_photo
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


def send_email_helper(posts_list, intros_list, close_posts, open_posts, bot):
    ''' foo creates users list and basic text of message like Title, etc'''

    time_zone = pytz.UTC
    now = time_zone.localize(datetime.utcnow())

    # users who paid
#    users_for_weekly_digest = User.objects.filter(tg_yesterday_best_posts=True
#                                                  ).filter(membership_expires_at__gte=now
#                                                           ).exclude(telegram_id=None
#                                                                     ).exclude(telegram_id='').all()

    users_for_weekly_digest = [User.objects.get(slug='romashovdmitryo')]

    # sending messages to users, who didn't pay
#    users_did_not_pay = User.objects.filter(membership_expires_at__lte=now).exclude(
#        telegram_id=None).exclude(telegram_id='').all()
    users_did_not_pay = [User.objects.get(slug='romashovdmitryo')]

    # 1. posts for paid ✅
    # 2. intros for paid ✅
    # 3. intros for NOT paid: ✅
    # 4. OPEN posts for NOT paid: ✅
    # 5. CLOSE posts for NOT paid: ✅

    if posts_list:
        # from querydict to list
        posts = [x['post'] for x in posts_list]
        dict_list_of_posts = []
        for object in posts:
            dict_list_of_posts.append({'text': construct_message(object), 'slug': {object.author.slug}})
            posts_string_for_bot = f'<strong>🔥 Лучшие посты клуба за прошедшую неделю 🚀</strong>'

        compile_message_helper(bot, users_for_weekly_digest, dict_list_of_posts, posts_string_for_bot)

    if intros_list:
        intros = [x['post'] for x in intros_list]
        intros_string_for_bot = f'<strong>😺 Самые интересные интро клуба за прошедшую неделю ❤️</strong>'
        dict_list_of_intros = []
        for object in intros:
            dict_list_of_intros.append({'text': construct_message(object), 'slug': {object.author.slug}})

        # send to paid users
        compile_message_helper(bot, users_for_weekly_digest, dict_list_of_intros, intros_string_for_bot)

        # and now send to NOT paid users
        if users_did_not_pay:
            intros_string_for_bot = '<strong>Это лучшие закрытые интро недели только для членов клуба. Вам они недоступны.'\
                'Если вы хотите получить к ним доступ, вы знаете, '\
                f'<a href="{settings.APP_HOST}/auth/login/?utm_source=private_bot_intro_pay">что делать</a></strong>.'
            # change all basic UTM to custom
            for obj in dict_list_of_intros:
                obj['text'] = obj['text'].replace('utm_source=private_bot_newsletter', 'utm_source=private_bot_intro_pay')

            optional = f'\n\n✅ <a href="{settings.APP_HOST}/auth/login/?utm_source=private_bot_intro_pay">Вступить в клуб</a>'
            compile_message_helper(bot, users_did_not_pay, dict_list_of_intros, intros_string_for_bot, optional)

    if close_posts and users_did_not_pay:
        close_posts = [x['post'] for x in close_posts]
        string_for_bot = '<strong>Это лучшие закрытые посты недели, только для членов клуба. '\
            'Вам они не доступны. Если вы хотите получить к ним доступ, вы знаете, '\
            f'<a href="{settings.APP_HOST}/auth/login/?utm_source=private_bot_closedpost_pay">что делать</a></strong>.'
        dict_list_close_posts = []
        for object in close_posts:
            dict_list_close_posts.append(
                {
                    'text': construct_message(
                        object=object,
                        custom_utm='utm_source=private_bot_closedpost_pay'
                    ),
                    'slug': {object.author.slug}
                }
            )

        optional = f'\n\n✅<a href="{settings.APP_HOST}/auth/login/?utm_source=private_bot_closedpost_pay">Вступить в клуб</a>'
        compile_message_helper(bot, users_did_not_pay, dict_list_close_posts, string_for_bot, optional)

    # for not paid users
    if open_posts and users_did_not_pay:
        open_posts = [x['post'] for x in open_posts]
        string_for_bot = f'<strong>🔥 Это лучшие открытые посты клуба за неделю 🚀</strong>'
        dict_list_open_posts = []
        for object in open_posts:
            dict_list_open_posts.append(
                {'text': construct_message(
                    object=object,
                    custom_utm='utm_source=private_bot_openpost_pay'
                ),
                    'slug': {object.author.slug}}
            )

        optional = f'\n\nЕсли вы хотите получить доступ к закрытым материалам клуба, вы знаете, что делать \n\n✅ <a href="{settings.APP_HOST}/auth/login/?utm_source=private_bot_openpost_pay">Вступить в клуб</a>'
        compile_message_helper(bot, users_did_not_pay, dict_list_open_posts, string_for_bot, optional)

class Command(BaseCommand):
    '''Foo creates list if best posts '''

    def handle(self, *args, **options):
        time_zone = pytz.UTC
        bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
        now = time_zone.localize(datetime.utcnow())
        week_ago = now - timedelta(days=200)
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
                                                      ).exclude(type='intro'
                                                                ).filter(author__in=User.objects.filter(Q(is_banned_until__lte=now) | Q(is_banned_until=None)).all()
                                                                         ).all()

        intros = Post.objects.filter(published_at__gte=week_ago_start
                                     ).filter(published_at__lte=week_ago_finish
                                              ).filter(is_approved_by_moderator=True
                                                       ).filter(type='intro'
                                                                ).filter(author__in=User.objects.filter(Q(is_banned_until__lte=now) | Q(is_banned_until=None)).all()
                                                                         ).all()

        # next content would be send to users who didn't pay. but we have thems telegran id
        # best close posts
        close_posts = Post.objects.filter(published_at__gte=week_ago_start
                                          ).filter(published_at__lte=week_ago_finish
                                                   ).filter(is_approved_by_moderator=True
                                                            ).exclude(type='intro'
                                                                      ).filter(is_public=False).filter(author__in=User.objects.filter(Q(is_banned_until__lte=now) | Q(is_banned_until=None)).all()
                                                                                                       ).all()

        # best open posts
        open_posts = Post.objects.filter(published_at__gte=week_ago_start
                                         ).filter(published_at__lte=week_ago_finish
                                                  ).filter(is_approved_by_moderator=True
                                                           ).exclude(type='intro'
                                                                     ).filter(is_public=True).filter(author__in=User.objects.filter(Q(is_banned_until__lte=now) | Q(is_banned_until=None)).all()
                                                                                                     ).all()

        posts_list = point_counter(posts)
        intros_list = point_counter(intros)
        close_posts_list = point_counter(close_posts)
        open_posts_list = point_counter(open_posts)

        if intros or posts or close_posts_list or open_posts_list:
            try:
                send_email_helper(posts_list, intros_list, close_posts_list, open_posts_list, bot)
            except Exception as e:
                MessageToDmitry(data='Что-то пошло не так! Ф-ция send_email_helper').send_message()
                MessageToDmitry(data=f'Ошибка: {e}').send_message()
