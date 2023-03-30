
# import Django packages
from django.core.management import BaseCommand

# import Models
from users.models.user import User
from users.models.random_coffee import RandomCoffee

# imports for getting config data
from club import settings

# Telegram imports
import telegram
from telegram import Update, ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

# import custom class for sending message
from bot.sending_message import TelegramCustomMessage


class Command(BaseCommand):

    def handle(self, *args, **options):

        user = User.objects.get(slug='romashovdmitryo')
        string_for_bot = 'string_for_bot'

        custom_message = TelegramCustomMessage(
            user=user,
            string_for_bot=string_for_bot
        )
        custom_message.send_count_to_dmitry(type_='done')