import json
from datetime import datetime, timedelta
from uuid import uuid4
from django.conf import settings
from base64 import b64encode
from django.core.management import BaseCommand
from users.models.user import User
from payments.models import Payment
from notifications.email.users import send_subscribe_8_email
from notifications.email.users import couldnd_withdraw_money_email
from notifications.email.users import cancel_subscribe_user_email
from notifications.telegram.users import subscribe_8_user
from notifications.telegram.users import couldnd_withdraw_money
from notifications.telegram.users import cancel_subscribe_user
from users.models.subscription_plan import SubscriptionPlan
from payments.unitpay import UnitpayService
from urllib.request import urlopen
from urllib.parse import quote
from notifications.telegram.common import Chat, send_telegram_message, ADMIN_CHAT


class Command(BaseCommand):
    help = "Fetches expiring accounts and tries to renew the subscription"

    def handle(self, *args, **options):

        expiring_users = User.objects.filter(membership_expires_at__gte=datetime.utcnow() + timedelta(days=8),
                                             membership_expires_at__lte=datetime.utcnow() + timedelta(days=9),
                                             unitpay_id__gt=0,
                                             moderation_status='approved',
                                             deleted_at__isnull=True)
        for user in expiring_users:
            self.stdout.write(f"Checking user: {user.slug}")
            payment_last = Payment.objects.filter(user_id=user.id, status='success').last()
            payment_json = json.loads(payment_last.data)
            send_subscribe_8_email(user, payment_last.amount, payment_json['params[purse]'])
            subscribe_8_user(user, payment_last.amount, payment_json['params[purse]'])
        self.stdout.write("Done 🥙")

        expiring_users = User.objects.filter(membership_expires_at__gte=datetime.utcnow() + timedelta(days=4),
                                             membership_expires_at__lte=datetime.utcnow() + timedelta(days=5),
                                             unitpay_id__gt=0,
                                             moderation_status='approved',
                                             deleted_at__isnull=True)
        for user in expiring_users:
            self.stdout.write(f"Checking user: {user.slug}")
            self.sendPayUnitpay(user)
        self.stdout.write("Done 🥙")

        expiring_users = User.objects.filter(membership_expires_at__gte=datetime.utcnow() + timedelta(days=3),
                                             membership_expires_at__lte=datetime.utcnow() + timedelta(days=4),
                                             unitpay_id__gt=0,
                                             moderation_status='approved',
                                             deleted_at__isnull=True)
        for user in expiring_users:
            self.stdout.write(f"Checking user: {user.slug}")
            self.sendPayUnitpay(user)
        self.stdout.write("Done 🥙")

        expiring_users = User.objects.filter(membership_expires_at__gte=datetime.utcnow() + timedelta(days=2),
                                             membership_expires_at__lte=datetime.utcnow() + timedelta(days=3),
                                             unitpay_id__gt=0,
                                             moderation_status='approved',
                                             deleted_at__isnull=True)
        for user in expiring_users:
            self.stdout.write(f"Checking user: {user.slug}")
            self.sendPayUnitpay(user)
        self.stdout.write("Done 🥙")

        expiring_users = User.objects.filter(membership_expires_at__gte=datetime.utcnow() + timedelta(days=1),
                                             membership_expires_at__lte=datetime.utcnow() + timedelta(days=2),
                                             unitpay_id__gt=0,
                                             moderation_status='approved',
                                             deleted_at__isnull=True)
        for user in expiring_users:
            self.stdout.write(f"Checking user: {user.slug}")
            self.sendPayUnitpay(user)
        self.stdout.write("Done 🥙")

        expiring_users = User.objects.filter(membership_expires_at__gte=datetime.utcnow() + timedelta(days=0),
                                             membership_expires_at__lte=datetime.utcnow() + timedelta(days=1),
                                             unitpay_id__gt=0,
                                             moderation_status='approved',
                                             deleted_at__isnull=True)
        for user in expiring_users:
            self.stdout.write(f"Checking user: {user.slug}")
            self.sendPayUnitpay(user)
        self.stdout.write("Done 🥙")

        expiring_users = User.objects.filter(membership_expires_at__gte=datetime.utcnow() + timedelta(days=-1),
                                             membership_expires_at__lte=datetime.utcnow() + timedelta(days=0),
                                             unitpay_id__gt=0,
                                             moderation_status='approved',
                                             deleted_at__isnull=True)
        for user in expiring_users:
            self.stdout.write(f"Checking user: {user.slug}")
            # self.cancelSubUser(user)
        self.stdout.write("Done 🥙")

    def insertUrlEncode(self, inserted, params):
        result = ''
        first = True
        for p in params:
            if first:
                first = False
            else:
                result += '&'
            result += inserted + '[' + p + ']=' + str(params[p])
        return result

    def sendPayUnitpay(self, user):
        payment_last = Payment.objects.filter(user_id=user.id, status='success',
                                              data__contains='subscriptionId').order_by('created_at').last()
        if payment_last:
            product = SubscriptionPlan.objects.filter(code=payment_last.product_code).last()
            order_id = uuid4().hex
            payment_json = json.loads(payment_last.data)
            cash = [{
                "name": "Sorokin.Club",
                "count": 1,
                "price": payment_last.amount,
                "type": "commodity",
            }]
            cash_items = quote(b64encode(json.dumps(cash).encode()))
            data = {
                "paymentType": payment_json['params[paymentType]'][0],
                "account": order_id,
                "sum": str(payment_last.amount),
                "projectId": 439242,
                "resultUrl": 'https://sorokin.club',
                "customerEmail": user.email,
                "currency": "RUB",
                "subscriptionId": user.unitpay_id,
                "desc": "Sorokin.Club",
                "ip": payment_json['params[ip]'][0],
                "secretKey": settings.UNITPAY_SECRET_KEY,
                "cashItems": cash_items
            }
            data["signature"] = UnitpayService.make_signature(data)
            payment = Payment.create(
                reference=order_id,
                user=user,
                product=product,
                data={},
            )
            requestUrl = 'https://unitpay.ru/api?method=initPayment&' + self.insertUrlEncode('params', data)
            response = urlopen(requestUrl)
            if response.status == 200:
                print("Success")
                text_send = '#Автосписание ' + user.email + " " + str(payment_last.amount)
                send_telegram_message(
                    chat=Chat(id=204349098),
                    text=text_send
                )
                send_telegram_message(
                    chat=ADMIN_CHAT,
                    text=text_send
                )
            else:
                couldnd_withdraw_money(user)
                couldnd_withdraw_money_email(user)

    def cancelSubUser(self, user):
        user.unitpay_id = ''
        user.save()
        cancel_subscribe_user(user)
        cancel_subscribe_user_email(user)
