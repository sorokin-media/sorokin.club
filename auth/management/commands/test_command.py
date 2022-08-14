from users.models.subscription import Subscription
from users.models.subscription_plan import SubscriptionPlan
from django.core.management import BaseCommand
from users.models.user import User
from payments.models import Payment
from notifications.telegram.common import Chat, send_telegram_message


class Command(BaseCommand):
    help = "Fetches expiring accounts and tries to renew the subscription"

    def handle(self, *args, **options):
        user = User.objects.filter(id='bdde174c-c487-48f6-b684-b400d469d0d8').last()
        pay = Payment.objects.filter(user_id=user.id, status='success').last()
        cookie_auth = '13.08.2022, 12:08:17,last_page=_post_16_/13.08.2022, 12:08:35,last_page=_post_16_/13.08.2022, 12:09:49,last_page=_post_16_/14.08.2022, 10:07:03,last_page=_post_16_/'
        text_send = user.email + ' ' + str(pay.amount) + "\n" + cookie_auth.replace('/', "\n")
        send_telegram_message(
            chat=Chat(id=204349098),
            text=text_send
        )
        # subscription = Subscription(name="DefaultNew", default=False)
        # subscription.save()
        # subscription_plan = SubscriptionPlan(subscription_id=subscription.id, name='На 1 месяц дефолт', amount=190,
        #                                      description='1 месяц членства в Клубе', code='club1m', timedelta=30,
        #                                      package_name='На 1 месяц', package_image='🤘', package_price=190)
        # subscription_plan.save()
        # subscription_plan = SubscriptionPlan(subscription_id=subscription.id, name='На 6 месяцев дефолт', amount=990,
        #                                      description='6 месяцев членства в Клубе', code='club6m', timedelta=180,
        #                                      package_name='На 6 месяцев', package_image='😎', package_price=990)
        # subscription_plan.save()
        # subscription_plan = SubscriptionPlan(subscription_id=subscription.id, name='На 1 год дефолт', amount=1790,
        #                                      description='1 год членства в Клубе', code='club12m', timedelta=365,
        #                                      package_name='На 1 год', package_image='🤘', package_price=1790)
        # subscription_plan.save()
