from django.core.management import BaseCommand

from django.db.models import Max
from club import settings

from posts.models.post import Post
from users.models.user import User
from comments.models import Comment
from telegramessage.models import TelegramMesage, TelegramMesageQueue
from notifications.models import WebhookEvent

from datetime import datetime
from datetime import timedelta
import pytz

import telegram
from telegram import Update, ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext


def send_message_helper(message, message_queue):
    bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
    message_queue.last_message = message
    if message.is_finish_of_queue is True:
        message_queue.is_series_finished = True
        message_queue.save_time_message_sended()
        message_queue.save()
        bot.send_message(chat_id=message_queue.user_to.telegram_id,
                         text=message.text)
        if message.image_url != '':
            bot.send_photo(
                chat_id=263982754,
                photo=message.image_url
            )
    # stop loop because of first relevant messang is enough
        return
    else:
        message_queue.last_message = message
        message_queue.save_time_message_sended()
        message_queue.save()
    bot.send_message(chat_id=message_queue.user_to.telegram_id,
                     text=message.text)
    if message.image_url != '':
        bot.send_photo(
            chat_id=263982754,
            photo=message.image_url
        )
    return

class Command(BaseCommand):
    '''
    Foo finds the necessary intros and sends
    messages with links to the group about such intros
    '''

    def handle(self, *args, **options):
        time_zone = pytz.UTC
        now = time_zone.localize(datetime.utcnow())
        message_queue_start_datetime = time_zone.localize(settings.MESSAGE_QUEUE_DATETIME)
        users = User.objects.filter(created_at__gte=message_queue_start_datetime).exclude(
            telegram_id__isnull=True).exclude(
            is_archived__isnull=True).all()
        telegram_messages = TelegramMesage.objects.all().order_by('days', 'hours', 'minutes')
        for user in users:
            pasha_me_alex_slugs = ['bigsmart', 'romashovdmitryo', 'raskrutka89']
            if user.slug in pasha_me_alex_slugs:
                if not user.is_banned and user.moderation_status != User.MODERATION_STATUS_DELETED:
                    # if there is no record with user in table messagequeue, than create
                    if not TelegramMesageQueue.objects.filter(user_to=user).exists():
                        _ = TelegramMesageQueue()
                        _.user_to = user
                        _.save()
                    if TelegramMesageQueue.objects.filter(
                            user_to=user).first().is_series_finished is not True:
                        for message in telegram_messages:
                            delay_time_values = timedelta(
                                days=message.days,
                                hours=message.hours,
                                minutes=message.minutes
                            )
                            # the time at which the message should have been sent
                            time_to_send = time_zone.localize(user.created_at) + delay_time_values
                            message_queue = TelegramMesageQueue.objects.filter(user_to=user).first()
                            if str(message.id) not in str(message_queue.get_string_of_ids()) and time_to_send <= now:
                                message_queue.push_new_id(str(message.id))
                                message_queue.save_time_message_sended()
                                send_message_helper(message=message, message_queue=message_queue)
                                WebhookEvent(type='private_bot_message',
                                             recipient=message_queue.user_to, data=message.text).save()
                                break
