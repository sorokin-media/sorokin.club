# Python imports
import logging
from typing import Dict

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


class Command(BaseCommand):
    """ Django command """

    def handle(self, *args, **options) -> None:
        """
        Start bot, that find users who didn't pay and remove them from chat. 

        There is no way to get chat_id of all members in chat
        because of default Telegram privacy rules.
        """
        users_telegram_id = User.objects.exclude(telegram_id__isnull=True).exclude(telegram_id='').values_list('telegram_id', flat=True)
        TELEGRAM_TOKEN_PAYMENT_BOT = "6808722895:AAESiT-izNKj_0chctWHmzOqAvgm16hRieg"
        bot = Bot(token=TELEGRAM_TOKEN_PAYMENT_BOT)
        chat_id = -1002010838055
        exception_list = ['vika', 'skorpion28', 'sesevor']
        message_text = """Эти ребята в чате, но срок аккаунта в клубе у них истек! 
                        Гоните их и насмехайтесь над ними!\n\n"""

        with open("output.txt", "w", encoding="utf-8") as output_file:
            [
                (output_file.write(
                    f"[obj in users_telegram_id] Type: {type(obj)}, obj: {obj}\n")
                )
                for obj in users_telegram_id
            ]
            chat_users = []
            for telegram_id in users_telegram_id:
                output_file.write(f"Telegram ID: {telegram_id}\n")
                telegram_user_info = try_except_helper(
                    bot=bot,
                    chat_id=chat_id,
                    user_id=telegram_id # отправялется один и тот же объект
                )

                if telegram_user_info:
                    output_file.write(
                            f"[telegram_user_info in users_telegram_user_info] Type: {type(telegram_user_info)}, obj: {telegram_user_info}\n"
                        )           
                    chat_users.append(telegram_user_info)
                else:
                    output_file.write(f"88 строка: {chat_id}, {telegram_id}")

            if chat_users:

                try:
                    [
                        output_file.write(
                            "Club user: " + User.objects.filter(telegram_id=chat_user['tg_id']).exclude(slug__in=exception_list).first().slug
                        )
                        for chat_user in chat_users
                        if User.objects.filter(telegram_id=chat_user['tg_id']).exclude(slug__in=exception_list).first() is not None \
                            and User.objects.filter(telegram_id=chat_user['tg_id']).exclude(slug__in=exception_list).exists()
                    ]
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
                    for user in expired_user_or_not:
                        output_file.write(f"\nExpired: {user}")
                    for username in expired_user_or_not:
                        message_text = message_text + "@" + username + "\n"

                    TelegramCustomMessage(
                        user=chat_id,
                        string_for_bot=message_text
                    )

                except Exception as ex:
                    log.error(f"\nException in pyament_bot: {ex}")
                    MessageToDmitry(data=f"error in expired_user_or_not. Ex: {ex}").send_message()
            else:
                MessageToDmitry(data="no users for payment bot")

        MessageToDmitry(data="finished").send_message()