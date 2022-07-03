import logging
import json
import hashlib
from uuid import uuid4
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

        expiring_users = User.objects.filter(email='raskrutka89@gmail.com')

        for user in expiring_users:
            self.stdout.write(f"Checking user: {user.slug}")
            payment_last = Payment.objects.filter(user_id=user.id, status='success', data__contains='subscriptionId').order_by('created_at').last()
            if payment_last:

                payment_data = {}
                product = PRODUCTS.get(payment_last.product_code)
                order_id = uuid4().hex

                payment = Payment.create(
                    reference=order_id,
                    user=user,
                    product=product,
                    data=payment_data,
                )
                pay_service = UnitpayService()
                invoice = pay_service.create_payment_subscribed(product, user, order_id)

        self.stdout.write("Done 🥙")
