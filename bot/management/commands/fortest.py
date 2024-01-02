
# import Django packages
from django.core.management import BaseCommand

# import Models
from users.models.user import User
from users.models.random_coffee import RandomCoffee

# Telegram imports
import telegram
from telegram import Update, ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

# imports for getting config data
from club import settings
from notifications.telegram.common import TELEGRAM_CLUB_MONEY_GROUP
from club.settings import TG_DEVELOPER_DMITRY

# import custom class for sending message
from bot.sending_message import TelegramCustomMessage
from notifications.telegram.common import send_telegram_message

class Command(BaseCommand):
    """ Django commands """
    def handle(self, *args, **options):
        """ testing bot """

        try:

            send_telegram_message(
                chat=TELEGRAM_CLUB_MONEY_GROUP,
                text=f"#тестработыбота",
            )

        except Exception:

            print(Exception)
