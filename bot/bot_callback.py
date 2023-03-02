from club import settings

import telegram
from telegram import Update, ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from users.models.user import User
from users.models.random_coffee import RandomCoffeeLogs, RandomCoffee


from django.db.models import Max

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
        bot.send_message(text='Как тебе собеседник? \n'
                         'Мы никому не расскажем, ответ нужен чтобы лучше подбирать тебе новых знакомых',
                         chat_id=user_telegram_id,
                         reply_markup=telegram.InlineKeyboardMarkup([*[
                             [telegram.InlineKeyboardButton("Очень интересный 🔥❤️🚀",
                                                            callback_data=f'coffee_grade:Очень интересный')],
                             [telegram.InlineKeyboardButton("Нормально 👍",
                                                            callback_data=f'coffee_grade:Нормально')],
                             [telegram.InlineKeyboardButton("Ничего особенного 🤷🏻‍♂️",
                                                            callback_data=f'coffee_grade:Ничего особенного')]
                         ]]))

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

'''
    message_id = update.callback_query.message.message_id
    chat_id = update.effective_user.id
    bot.delete_message(chat_id=chat_id, message_id=message_id)
'''
#    logs_string.save()
