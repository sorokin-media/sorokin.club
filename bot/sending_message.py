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

    logs_list = [TG_DEVELOPER_DMITRY] #, TG_ALEX]
    print('\n\nbot start\n\n')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    print('\n\nbot finish\n\n')
    COUNT_FOR_DMITRY = 0

    def __init__(self, etc='no data', buttons=None, photo=None, **kwargs) -> None:

        self.string_for_bot = kwargs['string_for_bot']
        self.etc = etc
        self.buttons = buttons
        self.photo = photo

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
            print(list_)
            self.buttons = telegram.InlineKeyboardMarkup([*list_])

        time.sleep(0.100)  # beacuse of API Telegram rules

        try:  # if reason in DB to an other, but in API rules
            message = self.bot.send_message(text=self.string_for_bot,
                                            photo=self.photo,
                                            chat_id=self.telegram_id,
                                            parse_mode=ParseMode.HTML,
                                            disable_web_page_preview=True,
                                            reply_markup=self.buttons
                                            )
            TelegramCustomMessage.COUNT_FOR_DMITRY += 1

            # for deleting message in future
            u = User.objects.get(telegram_id=self.telegram_id)
            random_coffee = RandomCoffee.objects.get(user=u)
            random_coffee.last_coffee_message_id = message['message_id']
            random_coffee.save()

        except Exception as error:
            try:  # if reason not in DB or an other, but in API rules
                if 'bot was blocked by the user' in str(error):
                    time.sleep(0.100)
                    self.string_for_bot = ''
                    for logs_user in self.logs_list:
                        self.bot.send_message(text='Бота заблокировал. '
                                              f'\Юзер: {self.slug}:'
                                              f'\nTelegram_id: {self.telegram_id}'
                                              f'\nTELEGRAM DATA: {self.telegram_data}'
                                              f'\nДопольнительная информация: {self.etc}',
                                              chat_id=logs_user
                                              )
                else:
                    time.sleep(300)
                    message = self.bot.send_message(text=self.string_for_bot,
                                                    photo=self.photo,
                                                    chat_id=self.telegram_id,
                                                    parse_mode=ParseMode.HTML,
                                                    disable_web_page_preview=True,
                                                    reply_markup=self.buttons
                                                    )

                    # for deleting message in future
                    u = User.objects.get(telegram_id=self.telegram_id)
                    random_coffee = RandomCoffee.objects.get(user=u)
                    random_coffee.last_coffee_message_id = message['message_id']
                    random_coffee.save()

                    for logs_user in self.logs_list:
                        self.bot.send_message(text='я поспал, я вернулся. Всё хорошо. '
                                              f'\nЮзер: {self.slug}:'
                                              f'\Дополнительная информация: {self.etc}',
                                              chat_id=logs_user
                                              )
                    TelegramCustomMessage.COUNT_FOR_DMITRY += 1
            except:  # if message was not sended as result
                self.string_for_bot = ''
                for logs_user in self.logs_list:
                    self.bot.send_message(text='Я вляпался в доупщит!'
                                          f'Вот ошибка: {error}\n\n'
                                          f'\nПроблемный юзер: {self.slug}:'
                                          f'\nЕго Telegram_id: {self.telegram_id}'
                                          f'\nTELEGRAM DATA: {self.telegram_data}'
                                          f'\nДополнительная информация: {self.etc}',
                                          chat_id=logs_user
                                          )

    def delete_message(self):

        u = User.objects.get(telegram_id=self.telegram_id)
        random_coffee = RandomCoffee.objects.get(user=u)
        telegram_id = int(self.telegram_id)

        if RandomCoffee.objects.filter(user=u).first().last_coffee_message_id:
            message_id = random_coffee.last_coffee_message_id
            self.bot.delete_message(chat_id=telegram_id, message_id=message_id)
            random_coffee.last_coffee_message_id = None
            random_coffee.save()

    def send_count_to_dmitry(self, type_=None):

        kek = self.logs_list['TG_DEVELOPER_DMITRY']
        print(f'\n\nLOGS USERS: {kek}\n ! ! ! ')
        print(f'SELF TYPE: {type_}')

        if type_ is not None:

            for logs_user in self.logs_list:

                self.bot.send_message(text=f'COUNT EQUAL TO: {TelegramCustomMessage.COUNT_FOR_DMITRY}\n'
                                      f'Тип рассылки: {type_}',
                                      chat_id=logs_user
                                      )
            TelegramCustomMessage.COUNT_FOR_DMITRY = 0
