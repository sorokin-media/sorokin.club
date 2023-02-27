from django.core.management import BaseCommand

# from django.db.models import Max
# from club import settings

from users.models.user import User
from posts.models.post import Post
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
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

class Command(BaseCommand):

    def handle(self, *args, **options):
        bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
        coffee_users = RandomCoffee.objects.filter(random_coffee_today=True).all()
        for coffee_user in coffee_users:
            coffee_buddy_id = coffee_user.random_coffee_last_partner_id
            coffee_buddy_full_name = User.objects.filter(id=coffee_buddy_id).first().full_name
            bot.send_message(text='<strong>Привет! Это бот Рандом Кофе!☕️</strong>\n\n'
                             f'Созвон с {coffee_buddy_full_name} прошёл успешно?',
                             parse_mode=ParseMode.HTML,
                             chat_id=coffee_user.user.telegram_id,
                             reply_markup=telegram.InlineKeyboardMarkup([*[
                                 [telegram.InlineKeyboardButton("Да, всё 🔥",
                                                                callback_data=f'coffee_feedback:Звонок состоялся')],
                                 [telegram.InlineKeyboardButton("Нет, по моей вине 😿",
                                                                callback_data=f'coffee_feedback:Я не позвонил')],
                                 [telegram.InlineKeyboardButton("Нет, с той стороны что-то пошло не так 😿",
                                                                callback_data=f'coffee_feedback:Собеседник не позвонил')]
                             ]]))


'''
Привет! Это бот Рандом Кофе.

Созвон с ИМЯ ФАМИЛИЯ прошел успешно?
Кнопки:
Да, все 🔥
Нет, по моей вине 😿
Нет, с той стороны что-то пошло не так 😿

select slug, random_coffee_today, random_coffee_past_partners, id, random_coffee_last_partner_id from users;
update users set random_coffee_is=True;
update users set random_coffee_today=True;
update users set random_coffee_past_partners=Null;
update users set random_coffee_last_partner_id=Null;
update users set slug='Lena' where slug='random_TaHpaaHQ2m';
'''
