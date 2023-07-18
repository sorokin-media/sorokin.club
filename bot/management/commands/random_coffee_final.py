
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
from bot.sending_message import TelegramCustomMessage, MessageToDmitry

class Command(BaseCommand):

    def handle(self, *args, **options):

        coffee_users = RandomCoffee.objects.filter(random_coffee_today=True).filter(random_coffee_is=True).all()
        log_for_dmitry = 'Это список всех, кто выбрался для сбора обратной связи: \n\n'
        log_for_dmitry += str([coffee_user.user.slug for coffee_user in coffee_users])
        MessageToDmitry(data=log_for_dmitry).send_message()
        for coffee_user in coffee_users:
            coffee_user.set_activity('go to try to send message')
            try:
                coffee_buddy_id = coffee_user.random_coffee_last_partner_id
                coffee_user.set_activity('come to condition')
                if coffee_buddy_id:
                    coffee_user.set_activity('condition done')
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
                    coffee_user.set_activity('come to message')
                    custom_message = TelegramCustomMessage(
                        user=coffee_user.user,
                        string_for_bot=text,
                        buttons=buttons,
                        random_coffee=True
                    )
                    custom_message.send_message()
                    coffee_user.set_activity('final message sended')
                    MessageToDmitry(data=f'Запрос отправлен юзеру {coffee_user.user.slug}.').send_message()

            except:
                coffee_user.set_activity('Final message was not sended! ')
                log_to_dmitry = f'Запрос не был отправлен юзеру: {coffee_user.user.slug}'
                MessageToDmitry(data=log_to_dmitry).send_message()

'''
typical commands for tests on local

update random_coffee set random_coffee_is=True;
update random_coffee set random_coffee_today=True;
update random_coffee set random_coffee_past_partners=Null;
update random_coffee set random_coffee_last_partner_id=Null;
update random_coffee set random_coffee_today=True;
select * from random_coffee;
'''
