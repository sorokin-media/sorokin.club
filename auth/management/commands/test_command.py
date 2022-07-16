from users.models.subscription import Subscription
from users.models.subscription_plan import SubscriptionPlan
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "Fetches expiring accounts and tries to renew the subscription"

    def handle(self, *args, **options):
        subscription = Subscription(name="Default", default=True)
        subscription.save()
        subscription_plan = SubscriptionPlan(subscription_id=subscription.id, name='На 1 год дефолт', amount=1200,
                                             description='1 год членства в Клубе', code='club12', timedelta=365,
                                             package_name='На 1 год', package_image='🤘', package_price=1200)
        subscription_plan.save()
        subscription_plan = SubscriptionPlan(subscription_id=subscription.id, name='На 2 года дефолт', amount=2400,
                                             description='2 года членства в Клубе', code='club24', timedelta=730,
                                             package_name='На 2 года', package_image='😎', package_price=2400)
        subscription_plan.save()
        subscription_plan = SubscriptionPlan(subscription_id=subscription.id, name='На 10 лет дефолт', amount=9000,
                                             description='10 год членства в Клубе', code='club120', timedelta=3650,
                                             package_name='На 10 лет', package_image='🚀', package_price=9000)
        subscription_plan.save()
