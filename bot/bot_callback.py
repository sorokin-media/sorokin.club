# imports for getting config data
from club import settings

# Telegram imports
import telegram
from telegram import Update, ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

# import Models
from users.models.user import User
from users.models.random_coffee import RandomCoffeeLogs, RandomCoffee

# Django ORM import
from django.db.models import Max

# import custom class for sending message
from bot.sending_message import TelegramCustomMessage


def no_random(update: Update, context: CallbackContext):
    bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
    callback_data = str(update.callback_query.data).replace("no_random_coffee ", "")
    user = User.objects.get(telegram_id=callback_data)
    random_coffee_string = RandomCoffee.objects.get(user=user.id)
    random_coffee_string.random_coffee_today = False
    random_coffee_string.save()
    message_id = update.callback_query.message.message_id
    chat_id = update.effective_user.id
    bot.delete_message(chat_id=chat_id, message_id=message_id)

def coffee_feedback(update: Update, context: CallbackContext):
    bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
    feedback = str(update.callback_query.data).replace("coffee_feedback:", "")
    feedback = {'first_reaction': feedback}
    user_telegram_id = update.effective_user.id
    user = User.objects.get(telegram_id=user_telegram_id)
    max_date_of_user = RandomCoffeeLogs.objects.filter(user=user).aggregate(Max('date'))['date__max']
    logs_string = RandomCoffeeLogs.objects.filter(user=user).filter(date=max_date_of_user).first()
    logs_string.feedback = feedback
    logs_string.save()
    message_id = update.callback_query.message.message_id
    bot.delete_message(chat_id=user_telegram_id, message_id=message_id)
    if feedback['first_reaction'] == 'Звонок состоялся':
        coffee_string = RandomCoffee.objects.get(user=user)
        coffee_string.coffee_done += 1
        coffee_string.save()

        text = 'Как тебе собеседник? \n'\
            'Мы никому не расскажем, ответ нужен чтобы лучше подбирать тебе новых знакомых'

        buttons = [
            {
                'text': 'Очень интересный 🔥❤️🚀',
                'callback': 'coffee_grade:Очень интересный'
            },
            {
                'text': 'Нормально 👍',
                'callback': 'coffee_grade:Нормально'
            },
            {
                'text': 'Ничего особенного 🤷🏻‍♂️',
                'callback': 'coffee_grade:Ничего особенного'
            }
        ]

        custom_message = TelegramCustomMessage(
            user=user,
            string_for_bot=text,
            buttons=buttons
        )
        custom_message.send_message()
        custom_message.COUNT_FOR_DMITRY()
    else:
        coffee_string = RandomCoffee.objects.get(user=user)
        coffee_string.coffee_deny += 1
        coffee_string.save()

def coffee_grade(update: Update, context: CallbackContext):
    bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
    feedback = str(update.callback_query.data).replace("coffee_grade:", "")
    user_telegram_id = update.effective_user.id
    user = User.objects.get(telegram_id=user_telegram_id)
    max_date_of_user = RandomCoffeeLogs.objects.filter(user=user).aggregate(Max('date'))['date__max']
    logs_string = RandomCoffeeLogs.objects.filter(user=user).filter(date=max_date_of_user).first()
    logs_string.feedback['second_reaction'] = feedback
    logs_string.save()
    message_id = update.callback_query.message.message_id
    bot.delete_message(chat_id=user_telegram_id, message_id=message_id)

    text = 'Спасибо, что делишься результатами! Это позволит мне обучиться и подбирать'\
        ' тебе самых интересных ребят для знакомства!\n\nНа следующей неделе я вернусь '\
        'с новым собеседником!'

    custom_message = TelegramCustomMessage(
        user=user,
        string_for_bot=text
    )

    custom_message.send_message()
    custom_message.send_count_to_dmitry()


'''
    message_id = update.callback_query.message.message_id
    chat_id = update.effective_user.id
    bot.delete_message(chat_id=chat_id, message_id=message_id)
'''
