# import Django packages
from django.core.management import BaseCommand
from django.db.models import Q

# import config
from club import settings

# import models
from users.models.user import User
from telegramessage.models import TelegramMesage, TelegramMesageQueue
from notifications.models import WebhookEvent

# Python imports
from datetime import datetime
from datetime import timedelta
import pytz
import re

# import telegram packages
import telegram
from telegram import Update, ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

# import custom class for sending messages by bot
from bot.sending_message import TelegramCustomMessage, MessageToDmitry

def construct_message(text):

    '''add UTM to links in text'''

    new_string = ''
    while 'https://sorokin' in text:
        x = re.search(r'https://sorokin[\w\d\=\:\/\.\?\-\&\%\;]+', text)
        start = x.start()
        finish = x.end()
        y = x.group()
        new_string = new_string + text[0:start] + y + '?utm_source=private_bot_messages_queue'
        text = text[finish:]
    new_string += text
    print('\n\n\nHUY PIZDA\n\n\n')
    return new_string

def send_message_helper(message, message_queue):

    message_queue.last_message = message
    text = construct_message(message.text)

    if message.is_finish_of_queue is True:

        message_queue.is_series_finished = True
        message_queue.save_time_message_sended()
        message_queue.save()

        if message.image_url is not None and message.image_url != '':

            custom_message = TelegramCustomMessage(
                user=message_queue.user_to,
                photo=message.image_url,
                string_for_bot=text
            )

            custom_message.send_photo()

        else:

            custom_message = TelegramCustomMessage(
                user=message_queue.user_to,
                string_for_bot=text
            )

            custom_message.send_message()

        custom_message.send_count_to_dmitry(type_=f'Очередь сообщений закончилась у юзера {message_queue.user_to.slug}')

    else:

        message_queue.last_message = message
        message_queue.save_time_message_sended()
        message_queue.save()

        if message.image_url is not None and message.image_url != '':

            custom_message = TelegramCustomMessage(
                user=message_queue.user_to,
                photo=message.image_url,
                string_for_bot=text
            )

            custom_message.send_photo()

        else:

            custom_message = TelegramCustomMessage(
                user=message_queue.user_to,
                string_for_bot=text
            )

            custom_message.send_message()

        custom_message.send_count_to_dmitry(type_=f'Очередь сообщения отправлена юзеру {message_queue.user_to.slug}')


class Command(BaseCommand):
    '''
    Foo finds the necessary intros and sends
    messages with links to the group about such intros
    '''

    def handle(self, *args, **options):

        time_zone = pytz.UTC
        now = time_zone.localize(datetime.utcnow())
        message_queue_start_datetime = time_zone.localize(settings.MESSAGE_QUEUE_DATETIME)

        # users that
        # 1) created after specify data
        # 2) not banned
        # 3) having bot
        users = User.objects.filter(
            created_at__gte=message_queue_start_datetime
        ).filter(
            Q(is_banned_until__lte=now) | Q(is_banned_until=None)
        ).filter(
            moderation_status='approved'
        ).exclude(
            telegram_id__isnull=True).all()

        if users:
            MessageToDmitry(data='Пользователи для очереди есть. ').send_message()

        # all writting messages
        telegram_messages = TelegramMesage.objects.all().order_by('days', 'hours', 'minutes')

        if telegram_messages:
            MessageToDmitry(data='Сообщения для очереди имеются. ').send_message()
        else:
            MessageToDmitry(data='Сообщений нет для пользователя. ').send_message()

        for user in users:

            # for tests on local
            # if user.slug == 'dev':

            # ONLY Dmirty on test on production
            pasha_me_alex_slugs = ['romashovdmitryo']

            # for tests on prod
#            pasha_me_alex_slugs = ['bigsmart', 'romashovdmitryo']
            if user.slug in pasha_me_alex_slugs:

                # if there is no record with user in table messagequeue, than create
                if not TelegramMesageQueue.objects.filter(user_to=user).exists():
                    _ = TelegramMesageQueue()
                    _.user_to = user
                    _.save()

                # if the user has not yet received the final message
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

                        # 1) if message is not in list of messages that was wended earlier
                        # 2) it's time to send a message
                        if str(message.id) not in str(message_queue.get_string_of_ids()) and time_to_send <= now:

                            if message.is_archived is not True:

                                message_queue.push_new_id(str(message.id))
                                message_queue.save_time_message_sended()

                                _ = 'Приложение пришло к этапу отправки сообщения из очереди. '
                                MessageToDmitry(data=_).send_message()

                                send_message_helper(message=message, message_queue=message_queue)

                                # saving data about event in table 'webhook_events', as written in task
                                WebhookEvent(
                                    type='private_bot_message',
                                    recipient=message_queue.user_to,
                                    data=message.text
                                ).save()

                                break

        MessageToDmitry(data='Очередь не отработала. Не прошла if-ы').send_message()
