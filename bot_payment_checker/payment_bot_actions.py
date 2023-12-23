# Python imports
import logging
from typing import Dict
import os
import sys

# import Django packages
import django
from django.core.management import BaseCommand
from django.db.models import Q

# IMPORTANT: this should go before any django-related imports (models, apps, settings)
# These lines must be kept together till THE END
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "club.settings")
django.setup()
# THE END

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

# import constants, config data
from bot_payment_checker.constants import SOROKIN_GROUPS

# import custom class for sending messages by bot
from bot.sending_message import TelegramCustomMessage, MessageToDmitry
from bot.sending_message import MessageToDmitry

log = logging.getLogger(__name__)


def try_except_helper(chat_id: int, user_id: str, bot: Bot) -> Dict[ChatMember, ChatMember]:
    """
    Foo-helper for using generator instead of for-loop.
    Foo check is there user in chat or not and return user's 
    Telegram data. 

    Parameters:
        chat_id (int): telegram id of chat where we want to check expired users
        user_id (str): telegram id of user who we want to check
    
    Returns:
        Dict[ChatMember.user.id, ChatMember.user.username]: dict with 
        telegram user account id and telegram account username
    """
    try:
        member_info = bot.get_chat_member(
            chat_id=chat_id,
            user_id=str(user_id)
        )
        tg_id = member_info.user.id
        tg_username = member_info.user.username
        return {
            "tg_id": tg_id,
            "tg_username": tg_username
        }
    except:
        pass

    return 

def search_for_unpaid_users(update: Update, context: CallbackContext) -> None:
    ''' foo searchs for users whi didn't pay '''

    log1 = str(update.message.chat_id)
    MessageToDmitry(data=f"LOG1 ----> {log1}").send_message()

    log2 = str(update.message.chat_id) in SOROKIN_GROUPS
    MessageToDmitry(data=f"LOG2 ----> {log2}").send_message()

    log3 = str(update.message.from_user.id)
    MessageToDmitry(data=f"LOG3 -----> {log3}").send_message()

    bool_result = (str(update.message.chat_id) in SOROKIN_GROUPS and str(update.message.from_user.id) in ["442442997"])
    MessageToDmitry(data=f"bool_result ----> {bool_result}")

    if (str(update.message.chat_id) in SOROKIN_GROUPS) and str(update.message.from_user.id) in ["442442997"]:

        users_telegram_id = User.objects.exclude(telegram_id__isnull=True).exclude(telegram_id='').values_list('telegram_id', flat=True)
        bot = Bot(token=settings.TELEGRAM_TOKEN)
        exception_list = ['vika', 'skorpion28', 'sesevor']
        message_text = (
            "<USERS>\nЭти ребята в чате, но срок аккаунта в клубе у них истек! \n"
            "Гоните их и насмехайтесь над ними!\n\n"
            "@bigsmart Алексей Сорокин\n"
            "@Golubova_Ann Нюта Голубова"
        )
        users_str = ""
        chat_id = str(update.message.chat_id)

        if chat_id in SOROKIN_GROUPS:

            chat_users = []

            for telegram_id in users_telegram_id:
                telegram_user_info = try_except_helper(
                    bot=bot,
                    chat_id=chat_id,
                    user_id=telegram_id  # отправялется один и тот же объект
                )

                if telegram_user_info:
                    chat_users.append(telegram_user_info)               

            if chat_users:

                try:

                    club_users = [
                        {
                            "club_user_obj": User.objects.filter(telegram_id=chat_user['tg_id']).exclude(slug__in=exception_list).first(),
                            "telegram_username": chat_user["tg_username"]
                        }
                        for chat_user in chat_users
                        if User.objects.filter(telegram_id=chat_user['tg_id']).exclude(slug__in=exception_list).exists() \
                            and User.objects.filter(telegram_id=chat_user['tg_id']).exclude(slug__in=exception_list).first() is not None
                    ]

                except Exception as ex:
                    log.error(f"\nException in pyament_bot: {ex}")
                    MessageToDmitry(data=f"error in club_users. Ex: {ex}").send_message()

                try:
                    expired_user_or_not = [
                        user["telegram_username"]
                        for user in club_users
                        if user["club_user_obj"].membership_days_left_round() < -10  # Перенесено условие в правильное место
                    ]
                    
                    if expired_user_or_not:

                        for username in expired_user_or_not:
                            users_str = users_str + "@" + username + "\n"

                        message_text = message_text.replace(
                            "<USERS>",
                            users_str
                        )
                        bot.send_message(
                            text=message_text,
                            chat_id=chat_id
                        )

                    else:
                        MessageToDmitry(data=f"no users for payment bot: {chat_id}").send_message()

                except Exception as ex:
                    log.error(f"\nException in pyament_bot: {ex}")
                    MessageToDmitry(data=f"error in expired_user_or_not. Ex: {ex}").send_message()

        MessageToDmitry(data="finished").send_message()
    
    else:
        MessageToDmitry(data="Кто-то пытается вызвать команду, кто доступа не имеет").send_message()