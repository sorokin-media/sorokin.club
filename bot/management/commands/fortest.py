
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

from club.settings import TG_DEVELOPER_DMITRY

import telegram
from telegram import Update, ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

class Command(BaseCommand):

    def handle(self, *args, **options):

        bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)

        try:

            u = User.objects.get(slug='Anna_Golubova')
            text = "Картинка Нюте! (:"
            chat_id = u.telegram_id
            photo = 'https://sorokin.club/static/images/random_coffee.jpg'

            bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=text,
                parse_mode=ParseMode.HTML)

        except Exception:

            print(Exception)
