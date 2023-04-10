# import Django packages
from django.core.management import BaseCommand

# import Models
from users.models.random_coffee import RandomCoffee

# import custom package for sending message
from bot.sending_message import TelegramCustomMessage


text_for_message = 'Привет! Напоминаю, что ты участвуешь в Random Coffee!\n' \
    'Если на этой неделе ты не хочешь ни с кем знакомиться, нажми кнопку👇 Ждем твоего ответа до 19-00 мск.'

class Command(BaseCommand):

    def handle(self, *args, **options):

        all_coffee_string = RandomCoffee.objects.all()
        all_coffee_string.update(random_coffee_last_partner_id=None)

        coffee_users = RandomCoffee.objects.filter(random_coffee_is=True).all()

        for coffee_user in coffee_users:
            coffee_user.random_coffee_today = True
            coffee_user.save()

            buttons = {}
            buttons['text'] = 'Я не готов на этой неделе 😿'
            buttons['callback'] = f'no_random_coffee {coffee_user.user.telegram_id}'
            buttons = [buttons]

            custom_message = TelegramCustomMessage(
                user=coffee_user.user,
                string_for_bot=text_for_message,
                buttons=buttons,
                random_coffee=True
            )

            custom_message.send_message()

        custom_message.send_count_to_dmitry(type_='Рассылка уведомления об участии в рандом-кофе')
