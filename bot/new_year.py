from bot.decorators import is_moderator

from posts.models.post import Post

import telegram
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

@is_moderator
def buddy_countering(update: Update, context: CallbackContext):
    slug_and_counter = Post.objects.filter(buddy_counter__gt=0).values('slug', 'buddy_counter')
    print(slug_and_counter)
    string_message = ''
    for _ in slug_and_counter:
        string_message = string_message + _['slug'] + ': ' + str(_['buddy_counter']) + '\n'
    update.effective_chat.send_message(text=string_message)
        