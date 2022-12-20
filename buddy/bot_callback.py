from django.db.models import Max
from club import settings

from posts.models.post import Post
from users.models.user import User
from comments.models import Comment

from datetime import datetime
from datetime import timedelta
import pytz

import telegram
from telegram import Update, ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

def buddy_get_task(update: Update, context: CallbackContext):
    '''
    Foo registrate time and account of buddy
    who gets obligation to ask question in intro
    '''
    callback_data = str(update.callback_query.data).replace("buddy_get_intro ", "")
    update.callback_query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([[
        InlineKeyboardButton(f"Вопрос задаст {update.effective_user.first_name} {update.effective_user.last_name}",
                             callback_data="no data")]]))
    update.effective_chat.id = update.effective_user.id
    post = Post.objects.filter(id=callback_data).first()
    responsible_buddy = User.objects.filter(telegram_id=str(update.effective_chat.id)).first()
    post.post_waits_buddy()  # set True on field
    post.appoint_as_responsible_buddy(responsible_buddy)  # set User on field
    post.set_time_start_buddy()
    post.message_id_to_buddy_group_from_bot = update.callback_query.message.message_id
    post.save()
    bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
    message_to_buddy = bot.send_message(chat_id=post.responsible_buddy.telegram_id,
                                        text='Теперь у тебя есть 3 часа, чтобы задать вопрос. '
                                             f'<a href=\"{settings.APP_HOST}/intro/{post.slug}\">Ссылка '
                                             'на интро</a>',
                                        parse_mode=ParseMode.HTML)
    post.message_id_to_responsible_buddy_user_from_bot = message_to_buddy['message_id']
    post.save()
