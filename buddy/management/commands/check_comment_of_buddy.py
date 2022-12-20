from django.core.management import BaseCommand

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


class Command(BaseCommand):
    '''
    Foo finds the necessary intros and sends
    messages with links to the group about such intros
    '''
    def handle(self, *args, **options):
        time_zone = pytz.UTC
        bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
        posts = Post.objects.filter(is_waiting_buddy_comment=True).all()
        if len(posts) > 0:
            for post in posts:
                time_of_buddy_start = time_zone.localize(post.buddy_comment_start)
                user_buddy = post.responsible_buddy
                now = time_zone.localize(datetime.utcnow())
                message_id_in_group = post.message_id_to_buddy_group_from_bot
                message_id_on_bot = post.message_id_to_responsible_buddy_user_from_bot
                delta = now - time_of_buddy_start
                if delta > timedelta(hours=3):
                    last_name = post.responsible_buddy.telegram_data['last_name']
                    first_name = post.responsible_buddy.telegram_data['first_name']
                    telegram_id = post.responsible_buddy.telegram_id
                    post.reset_buddy_status(task_status=False)
                    bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
                    bot.send_message(chat_id=-1001638622431,
                                     text=f'{first_name} {last_name} не задал вопрос вовремя, поэтому повторяем задачу!')
                    bot.send_message(chat_id=-1001638622431,
                                     parse_mode=ParseMode.HTML,
                                     text=f'Возращаемся к задаче! Давайте зададим вопрос пользователю. '
                                          f'<a href=\"{settings.APP_HOST}/intro/{post.slug}\">Ссылка '
                                          'на интро</a>',
                                     reply_markup=telegram.InlineKeyboardMarkup([
                                         *[
                                          [telegram.InlineKeyboardButton("Я задам! 💪",
                                           callback_data=f'buddy_get_intro {post.id}')]]]))
                    bot.delete_message(chat_id=-1001638622431, message_id=message_id_in_group)
                    bot.delete_message(chat_id=telegram_id, message_id=message_id_on_bot)
                elif Comment.objects.filter(author_id=user_buddy) \
                                    .filter(post_id=post.id).exists():
                    time_of_comment = Comment.objects.filter(author_id=user_buddy) \
                                                     .aggregate(Max('created_at'))
                    time_of_comment = time_of_comment["created_at__max"]
                    time_of_comment = time_zone.localize(time_of_comment)
                    # check for cases when comment is written not because of task
                    if time_of_comment > time_of_buddy_start:
                        telegram_id = post.responsible_buddy.telegram_id
                        user_buddy.buddy_increase_membership()
                        last_name = post.responsible_buddy.telegram_data['last_name']
                        first_name = post.responsible_buddy.telegram_data['first_name']
                        post.reset_buddy_status(task_status=True)
                        post.increment_buddy_counter()
                        bot.delete_message(chat_id=-1001638622431, message_id=message_id_in_group)
                        bot.delete_message(chat_id=telegram_id, message_id=message_id_on_bot)
                        buddy_days = user_buddy.membership_days_left_for_tg()
                        bot.send_message(chat_id=telegram_id,
                                         text='Спасибо, твой вопрос принят! В благодарность мы на день продлили твое участие в клубе! '
                                              f'Теперь у тебя их {buddy_days} ❤️')
                        bot.send_message(chat_id=-1001638622431,
                                         parse_mode=ParseMode.HTML,
                                         text=f'Новый успешный вопрос от {first_name} {last_name}. Спасибо, ты красава! ❤️ Так держать! 🚀')
