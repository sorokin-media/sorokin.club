# import Django packages
from django.core.management import BaseCommand

# import Models
from users.models.mute import Muted
from posts.models.post import Post
from users.models.random_coffee import RandomCoffee, RandomCoffeeLogs
from users.models.user import User

# imports for getting config data
from club import settings

# Telegram imports
import telegram
from telegram import Update, ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

# import custom package for sending message
from bot.sending_message import TelegramCustomMessage

# Python imports
from datetime import datetime
import pytz


class RandomCoffeeHelper:
    ''' make anything '''
    photo = 'https://sorokin.club/static/images/random_coffee.jpg'

    text_finish = '<strong>Вам нужно связаться и в личке договориться о созвоне.'\
        ' Назначайте удобное время и мессенджер для знакомства. '\
        'Созвониться вам нужно до вечера пятницы! 🔥</strong>\n\n'\
        'PS Мы настоятельно рекомендуем не просто переписываться текстом, а обязательно созваниваться с видео. '\
        'Текст передает только крупицу важной информации, звук - чуть больше,'\
        ' а с видео можно получить максимум,возможный на расстоянии ❤️'\


    def __init__(self, first_coffee_user: RandomCoffee, second_coffee_use: RandomCoffee) -> None:

        self.first_coffee_user = first_coffee_user
        self.second_coffee_user = second_coffee_use

    def send_message(self, coffee_user: RandomCoffee, coffee_buddy: RandomCoffee) -> None:
        ''' set, last partner id, make random cofee log and send message '''
        coffee_log = RandomCoffeeLogs()
        coffee_buddy_intro = Post.objects.filter(author=coffee_buddy.user).filter(type='intro').first()

        coffee_user.random_coffee_last_partner_id = coffee_buddy.user.id
        coffee_user.save()
    
        coffee_log.user = coffee_user.user
        coffee_log.user_buddy = coffee_buddy.user
        coffee_log.set_today_date()
        coffee_log.save()

        tg_link = coffee_buddy.random_coffee_tg_link
        if 'https://t.me/' in tg_link:
            tg_link = tg_link.replace('https://t.me/', '@')

        if tg_link[0] != '@':
            tg_link = '@' + tg_link

        text = '\n<strong>Привет! Это система Рандом Кофе!</strong>\n\n'\
            'Мы подобрали тебе собеседника на эту неделю! '\
            f'Это {coffee_buddy.user.full_name}!\n\n'\
            f'Интро: {settings.APP_HOST}/intro/{coffee_buddy_intro.slug}\n'\
            f'Телеграм для связи: {tg_link}\n\n'\
            f'{self.text_finish}'\

        custom_message = TelegramCustomMessage(
            user=coffee_user.user,
            string_for_bot=text,
            random_coffee=True,
            photo=self.photo
        )

        custom_message.delete_message()
        custom_message.send_photo()

    def set_partner(self, coffee_user: RandomCoffee, coffee_buddy: RandomCoffee) -> None:
        ''' set past_partner field in RandomCoffee '''
        if coffee_user.random_coffee_past_partners is None:
            coffee_user.random_coffee_past_partners = coffee_buddy.user.slug

        else:
            partners_1 = coffee_user.random_coffee_past_partners.split(', ')
            partners_1.append(coffee_buddy.user.slug)
            partners_1 = ', '.join(partners_1)
            coffee_user.random_coffee_past_partners = partners_1

        coffee_user.save()

    def process_data(self):
        ''' Main method of class which call other single methods '''
        self.set_partner(self.first_coffee_user, self.second_coffee_user)
        self.set_partner(self.second_coffee_user, self.first_coffee_user)

        self.first_coffee_user.random_coffee_last_partner_id = self.second_coffee_user.user.id
        self.second_coffee_user.random_coffee_last_partner_id = self.first_coffee_user.user.id

        self.first_coffee_user.save()
        self.second_coffee_user.save()

        self.send_message(self.first_coffee_user, self.second_coffee_user)
        self.send_message(self.second_coffee_user, self.first_coffee_user)

# CHANGE
# в переборе ниже есть случай, когда в выборку для рандом-кофе изначальную могут попадать
# юзеры, у которых окончилась подписка но оставлся подключенным рандом-кофе.
# с этим надо что-то придумать. Как-то изменить изначальную выбору, select-related
# или что-то такое использовать

class Command(BaseCommand):

    def handle(self, *args, **options):

        time_zone = pytz.UTC
        now = time_zone.localize(datetime.utcnow())

        coffee_users = list(RandomCoffee.objects.filter(random_coffee_today=True).filter(random_coffee_is=True).all())
        # look bellow, change that
        u_ = coffee_users[0].user
        k = 1
        # random_coffee_today True - user is not busy
        while len(coffee_users) >= 2:
            if k < len(coffee_users):
                # Fixing the issue with users whose membership has expired.
                expire_0 = time_zone.localize(coffee_users[0].user.membership_expires_at)
                expire_k = time_zone.localize(coffee_users[k].user.membership_expires_at)
                if expire_0 < now or coffee_users[0].user.is_banned:
                    coffee_users.pop(0)
                    coffee_users[0].random_coffee_today = False
                    # to catch bug
                    coffee_users[0].set_activity('random coffee set to False by membership')
                elif expire_k < now or coffee_users[k].user.is_banned:
                    coffee_users.pop(k)
                    coffee_users[0].random_coffee_today = False
                    # to catch bug
                    coffee_users[0].set_activity('random coffee set to False by user ban')
                elif coffee_users[k].random_coffee_past_partners is not None and\
                    coffee_users[0].random_coffee_past_partners is not None and\
                        (coffee_users[k].user.slug in coffee_users[0].random_coffee_past_partners or
                         (Muted.is_muted(
                             user_from=coffee_users[k].user,
                             user_to=coffee_users[0].user
                         ) or Muted.is_muted(
                             user_from=coffee_users[0].user,
                             user_to=coffee_users[k].user
                         ))):
                    k += 1
                else:
                    RandomCoffeeHelper(
                        first_coffee_user=coffee_users[0],
                        second_coffee_use=coffee_users[k]
                    ).process_data()
                    # catch bug
                    coffee_users[0].set_activity('message with partner was sended')
                    coffee_users[k].set_activity('message with partner was sended')
                    coffee_users.pop(k)
                    coffee_users.pop(0)
            else:
                coffee_users[0].random_coffee_last_partner_id = None
                coffee_users[0].random_coffee_today = False
                coffee_users[0].save()
                text = 'Извини, но на этой неделе не получилось подобрать тебе собеседника 😞'\
                    'На следующей неделе мы постараемся исправиться! ❤️'
                # catch bug
                coffee_users[0].set_activity('not found partner')
                custom_message = TelegramCustomMessage(
                    string_for_bot=text,
                    user=coffee_users[0].user
                )
                custom_message.delete_message()
                custom_message.send_message()
                coffee_users = coffee_users[1:]
                k = 1
        while coffee_users:
            u = coffee_users.pop(0)
            u.random_coffee_last_partner_id = None
            u.random_coffee_today = False
            u.save()
            u.set_activity('not found partner')
            text = 'Извини, но на этой неделе не получилось подобрать тебе собеседника 😞'\
                'На следующей неделе мы постараемся исправиться! ❤️'
            custom_message = TelegramCustomMessage(
                string_for_bot=text,
                user=u.user
            )
            custom_message.delete_message()
            custom_message.send_message()

        # CHANGE
        custom_message = TelegramCustomMessage(
            string_for_bot='',
            user=u_
        )

        custom_message.send_count_to_dmitry(type_='Всем участникам рандом-кофе отправили данные для созвона. ')
