import logging
import json
from datetime import datetime, timedelta

from django.core.management import BaseCommand
from users.models.user import User
from payments.models import Payment
from notifications.email.users import send_subscribe_8_email
from notifications.telegram.users import subscribe_8_user
from payments.unitpay import UnitpayService
from payments.products import PRODUCTS

class Command(BaseCommand):
    help = "Fetches expiring accounts and tries to renew the subscription"

    def handle(self, *args, **options):

        # expiring_users = User.objects.filter(membership_expires_at__gte=datetime.utcnow() + timedelta(days=8),membership_expires_at__lte=datetime.utcnow() + timedelta(days=9),unitpay_id__gt=0)
        #
        # for user in expiring_users:
        #     self.stdout.write(f"Checking user: {user.slug}")
        #     payment_last = Payment.objects.filter(user_id=user.id,status='success').last()
        #     payment_json = json.loads(payment_last.data)
        #     send_subscribe_8_email(user, payment_last.amount, payment_json['params[purse]'])
        #     subscribe_8_user(user, payment_last.amount, payment_json['params[purse]'])
        # self.stdout.write("Done 🥙")

        # expiring_users = User.objects.filter(
        #                                      email='dev@dev.dev')

        # for user in expiring_users:
        #     self.stdout.write(f"Checking user: {user.slug}")
        #     payment_last = Payment.objects.filter(user_id=user.id, status='success').order_by('created_at').last()
        #     payment_json = json.loads(payment_last.data)
        #     payment_data = {}
        #     product = PRODUCTS.get(payment_last.product_code)
        #     self.stdout.write(f"Checking user: {payment_last.created_at}")
            # pay_service = UnitpayService()
            #
            # invoice = pay_service.create_payment(product, user, True)
            #
            # payment = Payment.create(
            #     reference=invoice.id,
            #     user=user,
            #     product=product,
            #     data=payment_data,
            # )
        self.stdout.write("Done 🥙")
        PymentFull = Payment.objects.filter(id='d8273f41-263d-49a1-a99d-13a016b66525')
        for pay in PymentFull:
            paymentFull_json = json.loads(pay.data)

        paymentFind = Payment.objects.filter(id='93e7745c-7a3b-4958-b20a-61645acbef29')
        for pay in paymentFind:
            self.stdout.write(f"Pay oxyei: {pay.data}")
            payment_json = json.loads(pay.data)

            paymentFull_json.update(payment_json)
            print(repr(paymentFull_json))
            paymentFind.data = json.dumps(paymentFull_json)

            friend = json.loads(paymentFind.data)
            friend_email = friend.get("metadata", {}).get("invite") or friend.get("invite")
            print(repr(friend_email))
