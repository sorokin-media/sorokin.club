# Python imports
import logging
import os
import sys

# Django imports
import django

# IMPORTANT: this should go before any django-related imports (models, apps, settings)
# These lines must be kept together till THE END
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "club.settings")
django.setup()
# THE END

# Telegram imports
from django.conf import settings # that's for telegram too
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters, \
    CallbackQueryHandler

# import constants, config data
from bot_payment_checker.constants import SOROKIN_GROUPS

# import custom foos, classes
from bot_payment_checker.payment_bot_actions import search_for_unpaid_users

log = logging.getLogger(__name__)

def validate_group(update: Update, context: CallbackContext) -> bool:
    """Validate group: is it Sorokin's froup or not. """
    return update.message.chat_id in SOROKIN_GROUPS

def main() -> None:
    '''
        Start bot, that find users who didn't pay and remove them from chat. 

        There is no way to get chat_id of all members in chat
        because of default Telegram privacy rules.
    '''

    updater = Updater(settings.PAYMENT_BOT_TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(
        CommandHandler(
            "nonactive",  # command for bot reaction
            search_for_unpaid_users,  # call foo
#            Filters.chat(int(settings.TELEGRAM_ADMIN_CHAT_ID))  # validation for bot calls
        )
    )
    updater.start_polling()
    log.info(f"Start_polling payment Telegram bot. ")

    updater.idle()

if __name__ == '__main__':
    main()
