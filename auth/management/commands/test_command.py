from users.models.subscription import Subscription
from users.models.subscription_plan import SubscriptionPlan
from django.core.management import BaseCommand
from users.models.user import User
from posts.models.post import Post
from posts.models.subscriptions import PostSubscription
from payments.models import Payment
from notifications.telegram.common import Chat, send_telegram_message


class Command(BaseCommand):
    help = "Fetches expiring accounts and tries to renew the subscription"

    def handle(self, *args, **options):
        payment_last = Payment.objects.filter(status='success').order_by('created_at').last()
        date = str(payment_last.created_at)
        print('-'.join(date.split('.')[:-1]))
        a = '2022-10-12 10:04:04.542813'
        print('-'.join(a.split('.')[:-1]))

