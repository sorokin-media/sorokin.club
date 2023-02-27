from django.core.management import BaseCommand

# from django.db.models import Max
# from club import settings

from users.models.user import User
from users.models.random_coffee import RandomCoffee

from datetime import datetime
from datetime import timedelta
import pytz

from django.template import loader

from notifications.email.sender import send_club_email
from django.dispatch import receiver

from club import settings

import telegram
from telegram import Update, ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

text_for_message = 'Привет! Напоминаю, что ты участвуешь в Random Coffee!\n' \
    'Если на этой неделе ты не хочешь ни с кем знакомиться, нажми кнопку 👇 Ждем твоего ответа до 19 мск.'
# И кнопка - Я не готов на этой неделе 😿'

class Command(BaseCommand):

    def handle(self, *args, **options):
        bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
        coffee_users = RandomCoffee.objects.filter(random_coffee_is=True).all()
        for coffee_users in coffee_users:
            coffee_users.random_coffee_today = True
            coffee_users.save()
            bot.send_message(text=text_for_message,
                             chat_id=coffee_users.user.telegram_id,
                             reply_markup=telegram.InlineKeyboardMarkup([*[
                                 [telegram.InlineKeyboardButton("Я не готов на этой неделе 😿",
                                                                callback_data=f'no_random_coffee {coffee_users.user.telegram_id}')]]]))
