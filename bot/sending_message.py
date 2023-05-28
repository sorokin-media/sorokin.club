# Telegram imports
import telegram
from telegram import Update, ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

# time imports for pauses between sending messages
import time

# import models
from users.models.random_coffee import RandomCoffee
from users.models.user import User

# import static config data
from club.settings import TG_DEVELOPER_DMITRY, TG_ALEX, TELEGRAM_TOKEN

class TelegramCustomMessage():

    # don't touch, ask Alex about these list of accounts

    exception_list = ['vika', 'skorpion28', 'sesevor']

    logs_list = [TG_DEVELOPER_DMITRY, TG_ALEX]

    # FOR TEST WITHOUT ALEX
    # logs_list = [TG_DEVELOPER_DMITRY]#, TG_ALEX]
    # FOR TEST WITHOUT ALEX

    # for tests on local
    #logs_list = ['dev']

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    COUNT_FOR_DMITRY = 0

    def __init__(self, etc='no data', buttons=None, photo=None, random_coffee=False, **kwargs) -> None:

        self.string_for_bot = kwargs['string_for_bot']
        self.etc = etc
        self.buttons = buttons
        self.photo = photo
        self.random_coffee = random_coffee

        user = kwargs['user']

        self.telegram_id = user.telegram_id
        self.slug = user.slug
        self.telegram_data = user.telegram_data

    def send_message(self):

        if self.buttons:
            list_ = []
            for button in self.buttons:
                text = button['text']
                callback = button['callback']
                reply_markup = [telegram.InlineKeyboardButton(f"{text}",
                                                              callback_data=f"{callback}")]
                list_.append(reply_markup)
            self.buttons = telegram.InlineKeyboardMarkup([*list_])

        time.sleep(0.100)  # beacuse of API Telegram rules

        try:
            message = self.bot.send_message(text=self.string_for_bot,
                                            chat_id=self.telegram_id,
                                            parse_mode=ParseMode.HTML,
                                            disable_web_page_preview=True,
                                            reply_markup=self.buttons
                                            )
            TelegramCustomMessage.COUNT_FOR_DMITRY += 1

            # Random Coffee extension: for deleting message in future
            u = User.objects.get(telegram_id=self.telegram_id)
            # if user active in random coffee
            if self.random_coffee is True:
                if RandomCoffee.objects.filter(user=u).exists():
                    random_coffee = RandomCoffee.objects.get(user=u)
                    random_coffee.last_coffee_message_id = message['message_id']
                    random_coffee.save()

        except Exception as error:

            # if reason of error in API rules
            try:

                # if user block bot

                if 'bot was blocked by the user' in str(error):
                    self.string_for_bot = ''
                    # send logging message only to Dmitry
                    self.bot.send_message(text=f'Бота заблокировал юзер {self.slug}. ',
                                          chat_id=self.logs_list[0],
                                          parse_mode=ParseMode.HTML
                                          )

                # if there is any other reason neither blocking bot

                else:

                    # delete that only after Alex accept. Personal errors on one user.
                    if self.slug not in self.exception_list:

                        time.sleep(300)
                        message = self.bot.send_message(text=self.string_for_bot,
                                                        photo=self.photo,
                                                        chat_id=self.telegram_id,
                                                        parse_mode=ParseMode.HTML,
                                                        disable_web_page_preview=True,
                                                        reply_markup=self.buttons
                                                        )

                        # Random Coffee extension: for deleting message in future
                        u = User.objects.get(telegram_id=self.telegram_id)
                        # if user active in random coffee
                        if self.random_coffee is True:
                            if RandomCoffee.objects.filter(user=u).exists():
                                random_coffee = RandomCoffee.objects.get(user=u)
                                random_coffee.last_coffee_message_id = message['message_id']
                                random_coffee.save()

                        for logs_user in self.logs_list:
                            self.bot.send_message(text='я поспал, я вернулся. Всё хорошо. \n'
                                                  f'Юзер: {self.slug}\n'
                                                  f'Дополнительная информация: {self.etc}',
                                                  chat_id=logs_user,
                                                  parse_mode=ParseMode.HTML
                                                  )
                        TelegramCustomMessage.COUNT_FOR_DMITRY += 1

            # if message was not sended as result
            except Exception:

                # delete that only after Alex approve. Personal errors on one user.

                if self.slug not in self.exception_list:
                    self.string_for_bot = ''
                    for logs_user in self.logs_list:
                        self.bot.send_message(text='Произошло ошибка. Бот поставлен на паузу в 5 минут. \n\n'
                                              f'Вот ошибка: {error}\n\n'
                                              f'\nПроблемный юзер: {self.slug}:'
                                              f'\nЕго Telegram_id: {self.telegram_id}'
                                              f'\nTELEGRAM DATA: {self.telegram_data}'
                                              f'\nДополнительная информация: {self.etc}',
                                              chat_id=logs_user,
                                              parse_mode=ParseMode.HTML
                                              )
                    time.sleep(300)

    def send_photo(self):

        time.sleep(0.100)  # beacuse of API Telegram rules

        try:

            self.bot.send_photo(
                chat_id=self.telegram_id,
                photo=self.photo,
                caption=self.string_for_bot,
                parse_mode=ParseMode.HTML)

            TelegramCustomMessage.COUNT_FOR_DMITRY += 1

        except Exception as error:

            # if reason of error in API rules

            try:

                # if user block bot

                if 'bot was blocked by the user' in str(error):

                    self.string_for_bot = ''

                    # send logging message only to Dmitry
                    self.bot.send_message(text=f'Бота заблокировал юзер {self.slug}. ',
                                          chat_id=self.logs_list[0],
                                          parse_mode=ParseMode.HTML
                                          )

                # if there is any other reason neither blocking bot

                else:

                    time.sleep(300)

                    self.bot.send_photo(
                        chat_id=self.telegram_id,
                        photo=self.photo,
                        caption=self.string_for_bot,
                        parse_mode=ParseMode.HTML)

                    for logs_user in self.logs_list:
                        self.bot.send_message(text='я поспал, я вернулся. Всё хорошо. \n'
                                              f'Юзер: {self.slug}\n'
                                              f'Дополнительная информация: {self.etc}',
                                              chat_id=logs_user,
                                              parse_mode=ParseMode.HTML
                                              )
                    TelegramCustomMessage.COUNT_FOR_DMITRY += 1

            # if message was not sended as result
            except Exception:

                # delete that only after Alex approve. Personal errors on one user.

                if self.slug not in self.exception_list:
                    self.string_for_bot = ''
                    for logs_user in self.logs_list:
                        self.bot.send_message(text='Произошло ошибка. Бот поставлен на паузу в 5 минут. \n\n'
                                              f'Вот ошибка: {error}\n\n'
                                              f'\nПроблемный юзер: {self.slug}:'
                                              f'\nЕго Telegram_id: {self.telegram_id}'
                                              f'\nTELEGRAM DATA: {self.telegram_data}'
                                              f'\nДополнительная информация: {self.etc}',
                                              chat_id=logs_user,
                                              parse_mode=ParseMode.HTML
                                              )
                    time.sleep(300)

    def delete_message(self):

        u = User.objects.get(telegram_id=self.telegram_id)
        random_coffee = RandomCoffee.objects.get(user=u)
        telegram_id = int(self.telegram_id)

        if RandomCoffee.objects.filter(user=u).first().last_coffee_message_id:

            try:
                message_id = random_coffee.last_coffee_message_id
                self.bot.delete_message(chat_id=telegram_id, message_id=message_id)
            except Exception:
                pass
        random_coffee.last_coffee_message_id = None
        random_coffee.save()

    def send_count_to_dmitry(self, type_=None):

        if type_ is not None:

            for logs_user in self.logs_list:

                if self.COUNT_FOR_DMITRY < 3:

                    self.bot.send_message(text=f'{type_}',
                                          chat_id=logs_user
                                          )
                else:

                    self.bot.send_message(text=f'COUNT EQUAL TO: {TelegramCustomMessage.COUNT_FOR_DMITRY}\n'
                                          f'Тип рассылки: {type_}',
                                          chat_id=logs_user
                                          )

            TelegramCustomMessage.COUNT_FOR_DMITRY = 0


class MessageToDmitry:
    ''' simple class for developer Dmitry '''
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    dmitry = TG_DEVELOPER_DMITRY

    def __init__(self, data):

        self.data = data

    def send_message(self):

        self.bot.send_message(
            text=self.data,
            chat_id=self.dmitry
        )
