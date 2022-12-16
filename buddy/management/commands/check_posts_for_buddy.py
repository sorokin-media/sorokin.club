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

def send_to_buddy_group(bot, slug, intro_id, lattest_action):
    '''Foo for sending message to group '''
    time_zone = pytz.UTC
    # if user is created after 02.12.2022 (2 December 2022)
    author_id = Post.objects.filter(id=intro_id).first().author.id
    time_user_created = User.objects.filter(id=author_id).first().created_at
    time_user_created = time_zone.localize(time_user_created)
    time_start_buddy_project = time_zone.localize(datetime(year=2022, month=12, day=2))
    if time_user_created > time_start_buddy_project:
        time_membership_expires = User.objects.filter(id=author_id).first().membership_expires_at
        time_membership_expires = time_zone.localize(time_membership_expires)
        # if user is active
        if time_membership_expires > time_zone.localize(datetime.utcnow()):
            # if user is authorized in telegram bot
            if User.objects.filter(id=author_id).first().telegram_id:
                # if intro is approved
                if Post.objects.filter(id=intro_id).first().is_approved_by_moderator is True:
                    utc_comment_time = time_zone.localize(lattest_action)
                    utc_time_to_comment = time_zone.localize(datetime.utcnow()-timedelta(hours=2))
                    if utc_comment_time < utc_time_to_comment:
                        post = Post.objects.filter(id=intro_id).first()
                        if post.time_task_sended is not None:
                            time_to_send_tusk = time_zone.localize(datetime.utcnow()-timedelta(hours=3))
                            time_tusk_was_sended = time_zone.localize(post.time_task_sended)
                            if time_tusk_was_sended < time_to_send_tusk:
                                post.set_time_for_tusk()                
                                message = bot.send_message(chat_id=-1001638622431,
                                                           parse_mode=ParseMode.HTML,
                                                           text=f'Пользователю никто не написал по итогу предыдущего задания! \n'
                                                                'Давайте расспросим его!\n'
                                                                f'<a href=\"{settings.TELEGRAM_BOT_WEBHOOK_HOST}/intro/{slug}\">Ссылка '
                                                                'на интро</a>',
                                                           reply_markup=telegram.InlineKeyboardMarkup([
                                                                *[
                                                                 [telegram.InlineKeyboardButton("Я задам! 💪",
                                                                  callback_data=f'buddy_get_intro {intro_id}')]]]))
                                post.message_id_to_buddy_group_from_bot = message['message_id']
                                post.save()
                        else:
                            post.set_time_for_tusk()
                            message = bot.send_message(chat_id=-1001638622431,
                                                       parse_mode=ParseMode.HTML,
                                                       text='Пользователь два часа без комментариев 😮\n'
                                                            'Давайте расспросим его!\n'
                                                            f'<a href=\"{settings.APP_HOST}/intro/{slug}\">Ссылка '
                                                            'на интро</a>',
                                                       reply_markup=telegram.InlineKeyboardMarkup([
                                                           *[
                                                            [telegram.InlineKeyboardButton("Я задам! 💪",
                                                             callback_data=f'buddy_get_intro {intro_id}')]]]))
                            post.message_id_to_buddy_group_from_bot = message['message_id']
                            post.save()

class Command(BaseCommand):
    '''
    Foo finds the necessary intros and sends
    messages with links to the group about such intros
    '''
    def handle(self, *args, **options):
        bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
        # get intros with <= 7 buddy_counter
        zero_buddy_counter = Post.objects.all().filter(type='intro') \
                                               .filter(buddy_counter__lte=7) \
                                               .filter(is_waiting_buddy_comment=False)
        for intro in zero_buddy_counter:
            # get time of latest comment
            lattest_action = Comment.objects.filter(post_id=intro) \
                                            .values('id') \
                                            .annotate(Max('created_at'))
            # if there is a comment
            if lattest_action:
                lattest_action = lattest_action[0]['created_at__max']
            # if there is no, than get time of intro was created at
            else:
                lattest_action = intro.created_at
            send_to_buddy_group(bot=bot,
                                slug=intro.slug,
                                intro_id=intro.id,
                                lattest_action=lattest_action)
