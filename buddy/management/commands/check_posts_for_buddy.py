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

def send_to_buddy_group(bot, hours, hours_words, slug, intro_id, lattest_action):
    '''Foo for sending message to group '''
    time_zone = pytz.UTC
    # if user is created after 25.11.2022 (13 December 2022)
    author_id = Post.objects.filter(id=intro_id).first().author.id
    time_user_created = User.objects.filter(id=author_id).first().created_at
    time_user_created = time_zone.localize(time_user_created)
    time_start_buddy_project = time_zone.localize(datetime(year=2022, month=11, day=25))
    if time_user_created > time_start_buddy_project:
        # if user is authorized in telegram bot
        if User.objects.filter(id=author_id).first().telegram_id:
            utc_comment_time = time_zone.localize(lattest_action)
            utc_time_to_comment = time_zone.localize(datetime.utcnow()-timedelta(hours=hours))
            if utc_comment_time < utc_time_to_comment:
                post = Post.objects.filter(id=intro_id).first()
                if post.time_task_sended:
                    time_to_send_tusk = time_zone.localize(datetime.utcnow()-timedelta(hours=12))
                    time_tusk_was_sended = time_zone.localize(post.time_task_sended)
                    if time_tusk_was_sended < time_to_send_tusk:
                        post.set_time_for_tusk()                
                        bot.send_message(chat_id=446209536,
                                         parse_mode=ParseMode.HTML,
                                         text=f'Пользователю никто не написал по итогу предыдущего задания! \n'
                                              'Давайте расспросим его!\n'
                                              f'<a href=\"{settings.APP_HOST}/intro/{slug}\">Ссылка '
                                              'на интро</a>',
                                         reply_markup=telegram.InlineKeyboardMarkup([
                                             *[
                                              [telegram.InlineKeyboardButton("Я задам! 💪",
                                               callback_data=f'buddy_get_intro {intro_id}')]]]))
                else:
                    post.set_time_for_tusk()
                    bot.send_message(chat_id=446209536,
                                     parse_mode=ParseMode.HTML,
                                     text=f'{hours_words} без комментариев 😮\n'
                                          'Давайте расспросим его!\n'
                                          f'<a href=\"{settings.APP_HOST}/intro/{slug}\">Ссылка '
                                          'на интро</a>',
                                     reply_markup=telegram.InlineKeyboardMarkup([
                                         *[
                                          [telegram.InlineKeyboardButton("Я задам! 💪",
                                           callback_data=f'buddy_get_intro {intro_id}')]]]))

class Command(BaseCommand):
    '''
    Foo finds the necessary intros and sends
    messages with links to the group about such intros
    '''
    def handle(self, *args, **options):
        bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
        # get intros with zero questions from buddy
        zero_buddy_counter = Post.objects.all().filter(type='intro') \
                                               .filter(buddy_counter=0) \
                                               .filter(is_waiting_buddy_comment=False)
        for intro in zero_buddy_counter:
            # in this case we need to know time of post
            time_of_post = intro.created_at
            send_to_buddy_group(bot=bot,
                                hours=2,
                                hours_words='У нас новый пользователь! И он уже два часа',
                                slug=intro.slug,
                                intro_id=intro.id,
                                lattest_action=time_of_post)
        # get intros with > 0 comments from buddy
        zero_buddy_counter = Post.objects.all().filter(type='intro') \
                                               .filter(buddy_counter__gte=1) \
                                               .filter(buddy_counter__lte=7) \
                                               .filter(is_waiting_buddy_comment=False)
        for intro in zero_buddy_counter:
            # get time and date of latest comment from intro
            lattest_action = Comment.objects.filter(post_id=intro) \
                                            .values('id') \
                                            .annotate(Max('created_at'))
            lattest_action = lattest_action[0]['created_at__max']
            send_to_buddy_group(bot=bot,
                                hours=9,
                                hours_words='Пользователь уже девять часов',
                                slug=intro.slug,
                                intro_id=intro.id,
                                lattest_action=lattest_action)
