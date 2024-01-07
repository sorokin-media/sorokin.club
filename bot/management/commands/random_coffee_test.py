# import Django packages
from django.core.management import BaseCommand

# import Models
from users.models.random_coffee import RandomCoffee

# import custom package for sending message
from bot.sending_message import TelegramCustomMessage, MessageToDmitry


text_for_message = 'Привет! Напоминаю, что ты участвуешь в Random Coffee!\n' \
    'Если на этой неделе ты не хочешь ни с кем знакомиться, нажми кнопку👇 Ждем твоего ответа до 19-00 мск.'

class Command(BaseCommand):

    def handle(self, *args, **options):

        coffee_users = RandomCoffee.objects.filter(random_coffee_is=True).all()

        for coffee_user in coffee_users:

            if not coffee_user.user.membership_expires_is():

                test_message = (
                    str(coffee_user.user.slug) + ": " + str(coffee_user.user) + "\n"
                    "random_coffee_last_partner_id: " + str(coffee_user.random_coffee_last_partner_id)  + '\n'
                    "coffee_user.user.membership_expires_is(): " + str(coffee_user.user.membership_expires_is()) + "\n"
                )
                MessageToDmitry(data=test_message).send_message()

        MessageToDmitry(data=Exception).send_message()
