# import Django packages
from django.core.management import BaseCommand
from django.db.models import Q

# import config
from club import settings

# import models


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


# import custom class for sending messages by bot
from bot.sending_message import TelegramCustomMessage, MessageToDmitry


class Command(BaseCommand):
    ''' Django command '''

    def handle(self, *args, **options):
        ''' start bot, that find users who didn't 
            pay and remove them from chat 
        '''
        TELEGRAM_TOKEN_PAYMENT_BOT = "6808722895:AAESiT-izNKj_0chctWHmzOqAvgm16hRieg"
        bot = Bot(token=TELEGRAM_TOKEN_PAYMENT_BOT)
        chat_id = -1002010838055
        bot.get_chat_member