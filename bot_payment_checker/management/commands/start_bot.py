# import Django packages
from django.core.management import BaseCommand
from django.db.models import Q

# import config
from club import settings

# import models
from users.models.user import User

# Python imports
from datetime import datetime
from datetime import timedelta
import pytz
import re

# import telegram packages
from django.conf import settings
from telegram import Update, ParseMode, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters, \
    CallbackQueryHandler
from telegram import ChatMember

# import custom class for sending messages by bot
from bot.sending_message import TelegramCustomMessage, MessageToDmitry


def try_except_helper(chat_id: int, user_id: int, bot: Bot) -> ChatMember:
    ''' helper for using generator instead of for-loop '''
    try:
        return bot.get_chat_member(
            chat_id=chat_id,
            user_id=user_id
        ).user.id
    except:
        pass

class Command(BaseCommand):
    ''' Django command '''

    def handle(self, *args, **options):
        ''' start bot, that find users who didn't
            pay and remove them from chat

            There is no way to get chat_id of all members in chat
            because of default Telegram privacy rules.
        '''
        users_telegram_id = User.objects.all().values_list('telegram_id')
        TELEGRAM_TOKEN_PAYMENT_BOT = "6808722895:AAESiT-izNKj_0chctWHmzOqAvgm16hRieg"
        bot = Bot(token=TELEGRAM_TOKEN_PAYMENT_BOT)
        chat_id = -1002010838055

        chat_users = [
            try_except_helper(
                bot=bot,
                chat_id=chat_id,
                user_id=telegram_id[0]
            )
            for telegram_id in users_telegram_id
        ]
        # TO FIX: if 2 users have same telegran_id? 
        club_users = [
            User.objects.filter(telegram_id=telegram_id).first()
            for telegram_id in chat_users
        ]
        expired_user_or_not = [
            {user.telegram_id: user.membership_days_left_round()}
            for user in club_users
            if user.membership_days_left_round() < -10 # Перенесено условие в правильное место
        ]
        print(expired_user_or_not)
