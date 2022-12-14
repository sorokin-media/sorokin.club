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
    update.effective_chat.send_message(text='Теперь у тебя есть 3 часа, чтобы задать вопрос. '
                                            'Если вопрос задан, жмакни кнопку. '
                                            f'<a href=\"{settings.APP_HOST}/intro/{post.slug}\">Ссылка '
                                            'на интро</a>',
                                            parse_mode=ParseMode.HTML,
                                       reply_markup=telegram.InlineKeyboardMarkup([*[
                                            [telegram.InlineKeyboardButton(text="Готово!",
                                             callback_data=f"comment_done {post.id}"
                                                                           )]]]))
                                                                           
def start_buddy(update: Update, context: CallbackContext):
    callback_data = str(update.callback_query.data).replace("comment_done ", "")
    post = Post.objects.filter(id=callback_data).first()  # нашли пост
    user_buddy = Post.objects.filter(id=callback_data).first().responsible_buddy_id  # кто должен оставить комментарий
    if user_buddy:
        if Comment.objects.filter(author_id=user_buddy) \
                        .filter(post_id=post).exists():
            time_of_comment = Comment.objects.filter(author_id=user_buddy) \
                                             .aggregate(Max('created_at'))
            time_of_comment = time_of_comment["created_at__max"]
            time_of_buddy_start = Post.objects.filter(id=callback_data).first().buddy_comment_start
            time_zone = pytz.UTC
            time_of_comment = time_zone.localize(time_of_comment)
            time_of_buddy_start = time_zone.localize(time_of_buddy_start)
            if time_of_comment > time_of_buddy_start:
                user_buddy = User.objects.filter(id=user_buddy).first()
                user_buddy.buddy_increase_membership()
                update.effective_chat.id = user_buddy.telegram_id
                post.reset_buddy_status()
                post.increment_buddy_counter()
                update.callback_query.edit_message_reply_markup(reply_markup=None)
                update.effective_chat.send_message(text='Спасибо! В благодарность мы на день продлили твое участие в клубе!')
            else:
                user_buddy = User.objects.filter(id=user_buddy).first()
                update.effective_chat.id = user_buddy.telegram_id
                update.effective_chat.send_message(text='Что-то пошло не так, мы не видим твой коммент, попробуй еще раз и кнопка "Готово!"')
        else:
            user_buddy = User.objects.filter(id=user_buddy).first()
            update.effective_chat.id = user_buddy.telegram_id
            update.effective_chat.send_message(text='Что-то пошло не так, мы не видим твой коммент, попробуй еще раз и кнопка "Готово!"')
    else:
        update.effective_chat.send_message(text='Три часа прошло. Можешь снова взять на себя комментарий. ')