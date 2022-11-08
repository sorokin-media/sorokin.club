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
        payment_last = Payment.objects.filter(user_id='fadac4b3-152c-4181-8e5f-2269a2df9d95', status='success',
                                              data__contains='subscriptionId').order_by('created_at').last()
        print(payment_last.testttt)
        # users_query = User.objects.filter(is_email_verified=True)
        # for user in users_query:
        #     post_intro = Post.objects.filter(type='intro', author_id=user.id).last()
        #     if post_intro:
        #         subscribe_intro = PostSubscription.objects.filter(post_id=post_intro.id, user_id=user.id)
        #         if subscribe_intro:
        #             print('Есть')
        #         else:
        #             PostSubscription.subscribe(user, post_intro, type=PostSubscription.TYPE_ALL_COMMENTS)


#         user = User.objects.filter(id='bdde174c-c487-48f6-b684-b400d469d0d8').last()
#         pay = Payment.objects.filter(user_id=user.id, status='success').last()
#         cookie_auth = request.COOKIES['authUtmCookie']
#         if cookie_auth:
#             pay = Payment.objects.filter(user_id=user.id, status='success').last()
#             text_send = user.email + ' ' + str(pay.amount) + "\n" + cookie_auth.replace('/', "\n")
#             send_telegram_message(
#                 chat=Chat(id=204349098),
#                 text=text_send
#             )
#         subscription = Subscription(name="New08102022", default=False)
#         subscription.save()
#         subscription_plan = SubscriptionPlan(subscription_id=subscription.id, name='На 1 месяц', amount=420,
#                                              description='1 месяц членства в Клубе', code='club1m1022', timedelta=30,
#                                              package_name='На 1 месяц', package_image='🤘', package_price=420)
#         subscription_plan.save()
#         subscription_plan = SubscriptionPlan(subscription_id=subscription.id, name='На 1 год', amount=3920,
#                                              description='1 год членства в Клубе', code='club12m1022', timedelta=365,
#                                              package_name='На 1 год', package_image='🤘', package_price=3920)
#         subscription_plan.save()
#         subscription_plan = SubscriptionPlan(subscription_id=subscription.id, name='На 3 года', amount=7920,
#                                              description='3 года членства в Клубе', code='club12m1022', timedelta=1095,
#                                              package_name='На 3 года', package_image='🤘', package_price=7920)
#         subscription_plan.save()
