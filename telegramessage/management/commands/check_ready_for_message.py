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
    print('5')
    # если сообщение последнее, то и очередь закончилась, получается, выходит
    message_queue.last_message = message
    if message.is_finish_of_queue is True:
        message_queue.is_series_finished = True
        message_queue.save_time_message_sended()
        message_queue.save()
        bot.send_message(chat_id=message_queue.user_to.telegram_id,
                         text=message.name)
    # прекращаем обход сообщений, так как достаточно первого подходящего под условия
        return
    else:
        message_queue.last_message = message
        message_queue.save_time_message_sended()
        message_queue.save()
    bot.send_message(chat_id=message_queue.user_to.telegram_id,
                     text=message.name)
    return

class Command(BaseCommand):
    '''
    Foo finds the necessary intros and sends
    messages with links to the group about such intros
    '''

    def handle(self, *args, **options):
        time_zone = pytz.UTC
        now = time_zone.localize(datetime.utcnow())
        users = User.objects.all()
        print('1')
        # обходим каждого пользователя
        for user in users:
            if user.telegram_id:
                user_create_at = time_zone.localize(user.created_at)
                # проверяем чтобы зареган был после определенной даты
                if user_create_at > time_zone.localize(settings.MESSAGE_QUEUE_DATETIME):
                    # берём телеграмм сообщения, отсортированные дальности отправки, где сначала наименьшее
                    telegram_messages = TelegramMesage.objects.all().order_by('days', 'hours', 'minutes')
                    print('2')
                    if not TelegramMesageQueue.objects.filter(user_to=user).exists():
                        _ = TelegramMesageQueue()
                        _.user_to = user
                        _.save()
                    if TelegramMesageQueue.objects.filter(
                            user_to=user).first().is_series_finished is not True:
                        # обходим все сообщения, собираем с них задержку
                        print('3')
                        for message in telegram_messages:
                            delay_time_values = timedelta(
                                days=message.days,
                                hours=message.hours,
                                minutes=message.minutes
                            )
                            # определяем время, в которое следовало бы отправить уже сообщение
                            time_to_send = user_create_at + delay_time_values
                            # берём строку в таблице очередей
                            message_queue = TelegramMesageQueue.objects.filter(user_to=user).first()
    #                        if TelegramMesageQueue.objects.filter(user_to=user).first().last_time_message_sended is not None:
                            print(f"\n\nMESSAGE ID: {message.id}\n\n")
                            print(f'\n\nMESSAGE QUEUE: {message_queue.get_string_of_ids()}\n\n')
                            if str(message.id) not in str(message_queue.get_string_of_ids()) and time_to_send <= now:
                                print('hello')
                                message_queue.push_new_id(str(message.id))
                                message_queue.save_time_message_sended()
                                print(f"\n\nMESSAGE QUEREURUEQQERE {message_queue.id_of_sended_messages}\n\n")
                                send_message_helper(message=message, message_queue=message_queue)
                                WebhookEvent(type='private_bot_message', recipient=message_queue.user_to, data=message.text).save()
                                break
