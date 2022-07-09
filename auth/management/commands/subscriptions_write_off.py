import logging
import json
import hashlib
from uuid import uuid4
from datetime import datetime, timedelta
from uuid import uuid4
import requests
import socket
from django.conf import settings
from base64 import b64encode
from django.core.management import BaseCommand
from users.models.user import User
from payments.models import Payment
from notifications.email.users import send_subscribe_8_email
from notifications.telegram.users import subscribe_8_user
from payments.unitpay import UnitpayService
from payments.products import PRODUCTS
from pprint import pprint
from urllib.request import urlopen
from urllib.parse import quote

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

        # expiring_users = User.objects.filter(membership_expires_at__gte=datetime.utcnow() + timedelta(days=4),membership_expires_at__lte=datetime.utcnow() + timedelta(days=5),unitpay_id__gt=0)
        expiring_users = User.objects.filter(email='raskrutka89@gmail.com')

        for user in expiring_users:
            self.stdout.write(f"Checking user: {user.slug}")
            self.sendPayUnitpay(user)
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
            product = PRODUCTS.get(payment_last.product_code)
            order_id = uuid4().hex
            payment_json = json.loads(payment_last.data)
            cash = [{
                "name": "Сорокин.Клуб",
                "count": 1,
                "price": payment_last.amount,
                "type": "commodity",
            }]
            cash_items = quote(b64encode(json.dumps(cash).encode()))
            data = {
                "paymentType": payment_json['params[paymentType]'],
                "account": order_id,
                "sum": str(payment_last.amount),
                "projectId": 439242,
                "resultUrl": 'https://sorokin.club',
                "customerEmail": user.email,
                "currency": "RUB",
                "subscriptionId": user.unitpay_id,
                "desc": "Сорокин.Клуб",
                "ip": payment_json['params[ip]'],
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
            pprint(requestUrl)
            response = urlopen(requestUrl)
            pprint(response.read().decode('utf-8'))
