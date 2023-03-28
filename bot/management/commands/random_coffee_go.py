# import Django packages
from django.core.management import BaseCommand

# import Models
from users.models.mute import Muted
from posts.models.post import Post
from users.models.random_coffee import RandomCoffee, RandomCoffeeLogs

# imports for getting config data
from club import settings

# Telegram imports
import telegram
from telegram import Update, ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

# import custom package for sending message
from bot.sending_message import TelegramCustomMessage


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

def send_message_helper(user_1, user_2):
    # slug could be different for post and user, careful with that
    intro_1 = Post.objects.filter(author=user_1.user).filter(type='intro').first()
    intro_2 = Post.objects.filter(author=user_2.user).filter(type='intro').first()

    text_finish = '<strong>Вам нужно созвониться до вечера пятницы'\
        'Напоминаем: мы рекомендуем не просто переписываться текстом,'\
        'а обязательно созваниваться. Текст передает только крупицу важной'\
        'информации, звук - чуть больше, а с видео можно получить максимум,'\
        'возможный на расстоянии </strong>🔥🕒🔥'\

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

    #formatting for Telegram
    link_1 = user_1.random_coffee_tg_link
    link_2 = user_2.random_coffee_tg_link

    if link_1[0] != '@':
        link_1 = '@' + link_1
    if link_2[0] != '@':
        link_2 = '@' + link_2

    text = '\n<strong>Привет! Это система Рандом Кофе!</strong>\n\n'\
           'Мы подобрали тебе собеседника на эту неделю! '\
        f'Это {user_2.user.full_name}!\n\n'\
        f'Вот его интро: {settings.APP_HOST}/intro/{intro_2.slug}\n\n'\
        f'Вот его Телеграм для связи: {link_2}\n'\
        f'{text_finish}'\

    custom_message_1 = TelegramCustomMessage(
        user=user_1.user,
        string_for_bot=text
    )

    custom_message_1.send_message()

    text = '<strong>Привет! Это система Рандом Кофе!☕️</strong>\n'\
        'Мы подобрали тебе собеседника на эту неделю!'\
        f'Это {user_1.user.full_name}!\n\n'\
        f'Вот его интро: {settings.APP_HOST}/intro/{intro_1.slug}\n\n'\
        f'Вот его Телеграм для связи: {link_1}\n\n'\
        f'{text_finish}'

    custom_message_2 = TelegramCustomMessage(
        user=user_2.user,
        string_for_bot=text
    )

    custom_message_2.send_message()


class Command(BaseCommand):

    def handle(self, *args, **options):
        coffee_users = list(RandomCoffee.objects.filter(random_coffee_today=True).filter(random_coffee_is=True).all())
        # look bellow, change that
        u_ = coffee_users[0].user
        k = 1
        # random_coffee_today True - user is not busy
        while len(coffee_users) >= 2:
            if k < len(coffee_users):
                if coffee_users[k].random_coffee_past_partners is not None \
                        and coffee_users[0].random_coffee_past_partners is not None\
                        and coffee_users[k].user.slug in coffee_users[0].random_coffee_past_partners\
                        and (Muted.is_muted(
                            user_from=coffee_users[k].user,
                            user_to=coffee_users[0].user
                        ) or Muted.is_muted(
                            user_from=coffee_users[0].user,
                            user_to=coffee_users[k].user
                        )):
                    k += 1
                else:
                    coffee_partners_hepler(coffee_users[0], coffee_users[k])
                    send_message_helper(coffee_users[0], coffee_users[k])
                    coffee_users.pop(k)
                    coffee_users.pop(0)
            else:
                coffee_users[0].random_coffee_last_partner_id = None
                coffee_users[0].random_coffee_today = False
                coffee_users[0].save()
                text = 'Извини, но на этой неделе не получилось подобрать тебе собеседника 😞'\
                    'На следующей неделе мы постараемся исправиться! ❤️'
                custom_message = TelegramCustomMessage(
                    string_for_bot=text,
                    user=coffee_users[0].user
                )
                custom_message.send_message()
                coffee_users = coffee_users[1:]
                k = 1
        while coffee_users:
            u = coffee_users.pop(0)
            u.random_coffee_last_partner_id = None
            u.random_coffee_today = False
            u.save()
            text = 'Извини, но на этой неделе не получилось подобрать тебе собеседника 😞'\
                'На следующей неделе мы постараемся исправиться! ❤️'
            custom_message = TelegramCustomMessage(
                string_for_bot=text,
                user=u.user
            )
            custom_message.send_message()

        # change this one!
        custom_message = TelegramCustomMessage(
            string_for_bot='',
            user=u_
        )

        custom_message.send_count_to_dmitry(type_='Всем участникам рандом-кофе отправили данные для созвона. ')
