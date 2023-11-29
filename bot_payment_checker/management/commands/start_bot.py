# Python imports
import logging

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

def try_except_helper(chat_id: int, user_id: str, bot: Bot) -> ChatMember:
    ''' helper for using generator instead of for-loop '''
    try:
        return bot.get_chat_member(
            chat_id=chat_id,
            user_id=str(user_id)
        ).user.id

    except:
        pass


class Command(BaseCommand):
    ''' Django command '''

    def handle(self, *args, **options) -> None:
        ''' start bot, that find users who didn't
            pay and remove them from chat

            There is no way to get chat_id of all members in chat
            because of default Telegram privacy rules.
        '''
        users_telegram_id = User.objects.exclude(telegram_id__isnull=True).exclude(telegram_id='').values_list('telegram_id', flat=True)
        TELEGRAM_TOKEN_PAYMENT_BOT = "6808722895:AAESiT-izNKj_0chctWHmzOqAvgm16hRieg"
        bot = Bot(token=TELEGRAM_TOKEN_PAYMENT_BOT)
        chat_id = -1002010838055
        exception_list = ['vika', 'skorpion28', 'sesevor']

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
                telegram_id = try_except_helper(
                    bot=bot,
                    chat_id=chat_id,
                    user_id=telegram_id # отправялется один и тот же объект
                )

                if telegram_id:
                    output_file.write(
                            f"[telegram_id in users_telegram_id] Type: {type(telegram_id)}, obj: {telegram_id}\n"
                        )           
                    chat_users.append(telegram_id)
                else:
                    output_file.write("Nope\n")
            try:
                [
                    output_file.write(
                        User.objects.filter(telegram_id=telegram_id).exclude(slug__in=exception_list).first().slug
                    )
                    for telegram_id in chat_users
                    if User.objects.filter(telegram_id=telegram_id).exclude(slug__in=exception_list).first() is not None \
                        and User.objects.filter(telegram_id=telegram_id).exclude(slug__in=exception_list).exists()
                ]
                club_users = [
                    User.objects.filter(telegram_id=telegram_id).exclude(slug__in=exception_list).first() 
                    for telegram_id in chat_users
                    if User.objects.filter(telegram_id=telegram_id).exclude(slug__in=exception_list).exists() \
                        and User.objects.filter(telegram_id=telegram_id).exclude(slug__in=exception_list).first() is not None
                ]
            except Exception as ex:
                log.error(f"\nException in pyament_bot: {ex}")
                MessageToDmitry(data=f"error in club_users. Ex: {ex}").send_message()

            try:
                expired_user_or_not = [
                    {user.telegram_id: user.membership_days_left_round()}
                    for user in club_users
                    if user.membership_days_left_round() < -10 # Перенесено условие в правильное место
                ]
                for user in expired_user_or_not:
                    output_file.write(f"\nExpired: {str(user)}")
                [
                    MessageToDmitry(data=str(user)).send_message()
                    for user in expired_user_or_not
                ]

            except Exception as ex:
                log.error(f"\nException in pyament_bot: {ex}")
                MessageToDmitry(data=f"error in expired_user_or_not. Ex: {ex}").send_message()

        MessageToDmitry(data="finished").send_message()