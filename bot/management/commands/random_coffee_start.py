# import Django packages
from django.core.management import BaseCommand

# import Models
from users.models.random_coffee import RandomCoffee

# Telegram imports
import telegram
from telegram import Update, ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

# import custom package for sending message
from bot.sending_message import TelegramCustomMessage


text_for_message = 'Привет! Напоминаю, что ты участвуешь в Random Coffee!\n' \
    'Если на этой неделе ты не хочешь ни с кем знакомиться, нажми кнопку 👇 Ждем твоего ответа до 19 мск.'

class Command(BaseCommand):

    def handle(self, *args, **options):

        coffee_users = RandomCoffee.objects.filter(random_coffee_is=True).all()

        for coffee_user in coffee_users:
            coffee_user.random_coffee_today = True
            coffee_user.save()

            buttons = {}
            buttons['text'] = 'Я не готов на этой неделе 😿'
            buttons['callback'] = f'no_random_coffee {coffee_user.user.telegram_id}'
            buttons = [buttons]

#            print(f"\n\nDONE: {buttons['text']}\n\n")

            custom_message = TelegramCustomMessage(
                user=coffee_user.user,
                string_for_bot=text_for_message,
                buttons=buttons
            )

            custom_message.send_message()

        custom_message.send_count_to_dmitry(type_='Рассылка уведомления об участии в рандом-кофе')


'''
            try:
                bot.send_message(text=text_for_message,
                                 chat_id=coffee_users.user.telegram_id,
                                 reply_markup=telegram.InlineKeyboardMarkup([*[
                                     [telegram.InlineKeyboardButton("Я не готов на этой неделе 😿",
                                                                    callback_data=f'no_random_coffee {coffee_users.user.telegram_id}')]]]))
            except Exception as error:
                try:
                    if 'bot was blocked by the user' in str(error):
                        time.sleep(0.100)
                        bot.send_message(text='Я вляпался в доупщит!'
                                         f'Вот ошибка: {error}\n\n'
                                         f'\nПроблемный юзер: {coffee_users.user.slug}:'
                                         f'\nЕго Telegram_id: {coffee_users.user.telegram_id}'
                                         f'\nTELEGRAM DATA: {coffee_users.user.telegram_data}',
                                         chat_id=settings.TG_DEVELOPER_DMITRY
                                         )
                    else:
                        time.sleep(300)
                        bot.send_message(text=text_for_message,
                                         chat_id=coffee_users.user.telegram_id,
                                         reply_markup=telegram.InlineKeyboardMarkup([*[
                                             [telegram.InlineKeyboardButton("Я не готов на этой неделе 😿",
                                                                            callback_data=f'no_random_coffee {coffee_users.user.telegram_id}')]]]))
                        bot.send_message(text='я поспал, я вернулся. Всё хорошо. '
                                         f'\nЮзер: {coffee_users.user.slug}:',
                                         chat_id=settings.TG_DEVELOPER_DMITRY
                                         )
                except Exception as error:
                    bot.send_message(text='Я вляпался в доупщит!'
                                     f'Вот ошибка: {error}\n\n'
                                     f'\nПроблемный юзер: {coffee_users.user.slug}:'
                                     f'\nЕго Telegram_id: {coffee_users.user.telegram_id}'
                                     f'\nTELEGRAM DATA: {coffee_users.user.telegram_data}',
                                     chat_id=settings.TG_DEVELOPER_DMITRY
                                     )
        bot.send_message(text='рассылка рандом-кофе окончена',
                         chat_id=settings.TG_DEVELOPER_DMITRY
                         )
'''
