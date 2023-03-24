# Django core and Django ORM imports
from django.core.management import BaseCommand

# Django ORM imports
from django.db.models import Min

# import custom class for sending message in Telegram
from bot.sending_message import TelegramCustomMessage

# import Models
from telegramessage.models import DayHelpfulness
from users.models.user import User

# import custom package for sending message
from bot.sending_message import TelegramCustomMessage

class Command(BaseCommand):

    def handle(self, *args, **options):

        users = User.objects.filter(day_helpfullness_digest=True).all()

        if not DayHelpfulness.objects.filter(is_sended=False).exists():
            helpfullness = DayHelpfulness.objects.filter(is_sended=True).all()
            for _ in helpfullness:
                _.is_sended = False
                _.save()

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

        for user in users:

            custom_message = TelegramCustomMessage(
                string_for_bot=today_helpfullness.text,
                photo=today_helpfullness.image_url,
                user=user
            )
            custom_message.send_message()
        custom_message.send_count_to_dmitry(type_='Полезности дня. ')
