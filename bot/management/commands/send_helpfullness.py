# Django core and Django ORM imports
from django.core.management import BaseCommand

# Django ORM imports
from django.db.models import Min
from django.db.models import Q

# import custom class for sending message in Telegram
from bot.sending_message import TelegramCustomMessage

# import Models
from telegramessage.models import DayHelpfulness
from users.models.user import User

# import custom package for sending message
from bot.sending_message import TelegramCustomMessage

# Python imports: time and regex
from datetime import datetime
import pytz
import re

def construct_message(today_helpfullness):
    # divide text and name of message
    name = today_helpfullness.name
    # add UTM to every link in text of message
    text = today_helpfullness.text
    new_string = ''
    while 'https://sorokin' in text:
        x = re.search(r'https://sorokin[\w\d\=\:\/\.\?\-\&\%\;]+', text)
        start = x.start()
        finish = x.end()
        y = x.group()
        new_string = new_string + text[0:start] + y + '?utm_source=private_bot_newsletter'
        text = text[finish:]
    new_string += text
    text = f'<strong>{name}</strong>\n\n{new_string}'
    return text

class Command(BaseCommand):

    def handle(self, *args, **options):

        time_zone = pytz.UTC
        now = time_zone.localize(datetime.utcnow())

        # users who activate helpfulness digest and not banned
        users = User.objects.filter(
            day_helpfullness_digest=True
        ).filter(
            Q(is_banned_until__lte=now) | Q(is_banned_until=None)
        ).all()

        # if all message are have been sended already

        if not DayHelpfulness.objects.filter(is_sended=False).exists():

            helpfullness = DayHelpfulness.objects.filter(is_sended=True).all()

            for _ in helpfullness:
                _.is_sended = False
                _.save()

        # get message closest to zero by order 

        today_helpfullness = DayHelpfulness.objects.get(
            order=DayHelpfulness.objects.filter(
                is_sended=False,
                is_archived=False
            ).aggregate(
                Min('order')
            )['order__min']
        )

        today_helpfullness.is_sended = True
        today_helpfullness.save()

        text = construct_message(today_helpfullness)

        for user in users:

            custom_message = TelegramCustomMessage(
                string_for_bot=text,
                photo=today_helpfullness.image_url,
                user=user
            )

            if today_helpfullness.image_url:
                custom_message.send_photo()
            else:
                custom_message.send_message()

        if users:

            custom_message.send_count_to_dmitry(type_='Полезности дня. ')
        
