# Django core and Django ORM imports
from django.core.management import BaseCommand

# Django ORM imports
from django.db.models import Min
from django.db.models import Q

# import custom class for sending message in Telegram
from bot.sending_message import TelegramCustomMessage

# import Models
from bot.models.cool_intros import CoolIntro
from users.models.user import User

# import custom package for sending message
from bot.sending_message import TelegramCustomMessage

# Python imports: time and regex
from datetime import datetime
import pytz
import re

# for test
from club.settings import TG_ALEX, TG_DEVELOPER_DMITRY, TG_NUTA

def construct_message(text):

    '''add UTM to links in text'''

    new_string = ''
    while 'https://sorokin' in text:
        x = re.search(r'https://sorokin[\w\d\=\:\/\.\?\-\&\%\;]+', text)
        start = x.start()
        finish = x.end()
        y = x.group()
        new_string = new_string + text[0:start] + y + '?utm_source=private_bot_cool_intros'
        text = text[finish:]
    new_string += text
    return new_string

class Command(BaseCommand):

    def handle(self, *args, **options):

        time_zone = pytz.UTC
        now = time_zone.localize(datetime.utcnow())

        # users who activate helpfulness digest and not banned

#        users = User.objects.filter(
#            day_helpfullness_digest=True
#        ).filter(
#            Q(is_banned_until__lte=now) | Q(is_banned_until=None)
#        ).all()

        # for test on prod
#        dmitry = User.objects.get(telegram_id=TG_DEVELOPER_DMITRY)
#        alex = User.objects.get(telegram_id=TG_ALEX)
#        users = [dmitry, alex]

        # for test on local
        dmitry = User.objects.get(telegram_id=TG_DEVELOPER_DMITRY)
        nuta = User.objects.get(telegram_id=TG_NUTA)
        users = [dmitry, nuta]

        # if all message are have been sended already

        if not CoolIntro.objects.filter(is_sended=False).exists():

            cool_intros = CoolIntro.objects.filter(is_sended=True).all()

            for _ in cool_intros:
                _.is_sended = False
                _.save()

        # get message closest to zero by order

        cool_intro = CoolIntro.objects.get(
            order=CoolIntro.objects.filter(
                is_sended=False,
                is_archived=False
            ).aggregate(
                Min('order')
            )['order__min']
        )

        cool_intro.is_sended = True
        cool_intro.save()

        text = construct_message(cool_intro.text)
        image_url = cool_intro.image_url

        for user in users:

            if image_url is not None and image_url != '':

                custom_message = TelegramCustomMessage(
                    user=user,
                    photo=image_url,
                    string_for_bot=''
                )

                custom_message.send_photo()

                custom_message = TelegramCustomMessage(
                    user=user,
                    string_for_bot=text
                )

                custom_message.send_message()

            else:

                custom_message = TelegramCustomMessage(
                    user=user,
                    string_for_bot=text
                )

                custom_message.send_message()

        if users:

            custom_message.send_count_to_dmitry(type_='Крутая интруха отправлена. ')
