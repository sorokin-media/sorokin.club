from django.core.management import BaseCommand

# from django.db.models import Max
# from club import settings

from users.models.user import User
from posts.models.post import Post
from users.models.random_coffee import RandomCoffee, RandomCoffeeLogs

from datetime import datetime
from datetime import timedelta
import pytz

from django.template import loader

from notifications.email.sender import send_club_email
from django.dispatch import receiver

from club import settings

import telegram
from telegram import Update, ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

text_for_message = 'Привет! Напоминаю, что ты участвуешь в Random Coffee!\n' \
    'Если на этой неделе ты не хочешь ни с кем знакомиться, нажми кнопку 👇 Ждем твоего ответа до 19 мск.'
# И кнопка - Я не готов на этой неделе 😿'

def coffee_partners_hepler(user_1, user_2):
    if user_1.random_coffee_past_partners is None:
        user_1.random_coffee_past_partners = user_2.user.slug

    else:
        partners_1 = user_1.random_coffee_past_partners.split(', ')
        partners_1.append(user_2.user.slug)
        partners_1 = ', '.join(partners_1)
        user_1.random_coffee_past_partners = partners_1

    if user_2.random_coffee_past_partners is None:
        user_2.random_coffee_past_partners = user_1.user.slug

    else:
        partners_2 = user_2.random_coffee_past_partners.split(', ')
        partners_2.append(user_1.user.slug)
        partners_2 = ', '.join(partners_2)
        user_2.random_coffee_past_partners = partners_2

    user_1.save()
    user_2.save()

def send_message_helper(user_1, user_2, bot):
    # slug could be different for post and user, careful with that
    intro_1 = Post.objects.filter(author=user_1.user).filter(type='intro').first()
    intro_2 = Post.objects.filter(author=user_2.user).filter(type='intro').first()

    text_finish = 'Вам нужно созвониться до вечера пятницы'
    'Напоминаем: мы рекомендуем не просто переписываться текстом,'
    'а обязательно созваниваться. Текст передает только крупицу важной'
    'информации, звук - чуть больше, а с видео можно получить максимум,'
    'возможный на расстоянии.'

    user_1.random_coffee_last_partner_id = user_2.user.id
    user_2.random_coffee_last_partner_id = user_1.user.id

    user_1.save()
    user_2.save()

    coffee_log_1 = RandomCoffeeLogs()
    coffee_log_2 = RandomCoffeeLogs()

    coffee_log_1.user, coffee_log_2.user = user_1.user, user_2.user
    coffee_log_1.user_buddy, coffee_log_2.user_buddy = user_2.user, user_1.user
    coffee_log_1.set_today_date()
    coffee_log_2.set_today_date()
    coffee_log_1.save()
    coffee_log_2.save()

    bot.send_message(chat_id=user_1.user.telegram_id,
                     parse_mode=ParseMode.HTML,
                     text='<strong>Привет! Это система Рандом Кофе!</strong>\n\n'
                     'Мы подобрали тебе собеседника на эту неделю!'
                     f'Это {user_2.user.full_name}!\n\n'
                     f'Вот его интро: {settings.APP_HOST}/intro/{intro_2.slug}\n\n'
                     f'Вот его Телеграм для связи: {user_2.random_coffee_tg_link}\n'
                     f'{text_finish}')

    bot.send_message(chat_id=user_2.user.telegram_id,
                     parse_mode=ParseMode.HTML,
                     text='<strong>Привет! Это система Рандом Кофе!☕️</strong>\n'
                     'Мы подобрали тебе собеседника на эту неделю!'
                     f'Это {user_1.user.full_name}!\n\n'
                     f'Вот его интро: {settings.APP_HOST}/intro/{intro_1.slug}\n\n'
                     f'Вот его Телеграм для связи: {user_1.random_coffee_tg_link}\n\n'
                     f'{text_finish}')

class Command(BaseCommand):

    def handle(self, *args, **options):
        bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
#        coffee_users = list(RandomCoffee.objects.filter(random_coffee_today=False).filter(random_coffee_is=True).all())
        coffee_users = list(RandomCoffee.objects.filter(random_coffee_today=True).filter(random_coffee_is=True).all())
        k = 1
        # random_coffee_today True - user is not busy
        while len(coffee_users) >= 2:
            if k < len(coffee_users):
                if coffee_users[k].random_coffee_past_partners is not None \
                        and coffee_users[0].random_coffee_past_partners is not None\
                        and coffee_users[k].user.slug in coffee_users[0].random_coffee_past_partners:
                    k += 1
                else:
                    coffee_partners_hepler(coffee_users[0], coffee_users[k])
                    send_message_helper(coffee_users[0], coffee_users[k], bot)
                    coffee_users.pop(k)
                    coffee_users.pop(0)
            else:
                coffee_users[0].random_coffee_last_partner_id = None
                coffee_users[0].random_coffee_today = False
                coffee_users[0].save()
                bot.send_message(chat_id=coffee_users[0].user.telegram_id,
                                 text='Извини, но на этой неделе не получилось подобрать тебе собеседника 😞'
                                 'На следующей неделе мы постараемся исправиться! ❤️')
                coffee_users = coffee_users[1:]
                k = 1
        while coffee_users:
            u = coffee_users.pop(0)
            u.random_coffee_last_partner_id = None
            u.random_coffee_today = False
            u.save()
            bot.send_message(chat_id=u.user.telegram_id,
                             text='Извини, но на этой неделе не получилось подобрать тебе собеседника 😞'
                             'На следующей неделе мы постараемся исправиться! ❤️')


'''
select slug, random_coffee_today, random_coffee_past_partners, id, random_coffee_last_partner_id from;
update random_coffee set random_coffee_is=True;
update random_coffee set random_coffee_today=True;
update random_coffee set random_coffee_past_partners=Null;
update random_coffee set random_coffee_last_partner_id=Null;
update random_coffee set slug='Lena' where slug='random_TaHpaaHQ2m';
'''
