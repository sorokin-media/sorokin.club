
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

        coffee_users = RandomCoffee.objects.filter(random_coffee_today=True).filter(random_coffee_is=True).all()
        for coffee_user in coffee_users:
            coffee_buddy_id = coffee_user.random_coffee_last_partner_id
            coffee_buddy_full_name = User.objects.filter(id=coffee_buddy_id).first().full_name

            text = '<strong>Привет! Это бот Рандом Кофе!☕️</strong>\n\n'\
                f'Созвон с {coffee_buddy_full_name} прошёл успешно?'

            buttons = [
                {
                    'text': 'Да, всё 🔥',
                    'callback': 'coffee_feedback:Звонок состоялся'
                },
                {
                    'text': 'Нет, по моей вине 😿',
                    'callback': 'coffee_feedback:Я не позвонил'
                },
                {
                    'text': 'Нет, с той стороны что-то пошло не так 😿',
                    'callback': 'coffee_feedback:Собеседник не позвонил'
                }
            ]

            custom_message = TelegramCustomMessage(
                user=coffee_user.user,
                string_for_bot=text,
                buttons=buttons
                )
            custom_message.send_message()
        
        custom_message.send_count_to_dmitry(type_='Отправлен запрос на получение первого фидбека')



'''
typical commands for tests on local

update users set random_coffee_is=True;
update users set random_coffee_today=True;
update users set random_coffee_past_partners=Null;
update users set random_coffee_last_partner_id=Null;
'''
