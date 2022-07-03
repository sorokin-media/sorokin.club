import logging
import json
import hashlib
from uuid import uuid4
from datetime import datetime, timedelta
from uuid import uuid4
import requests
import socket
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

        # expiring_users = User.objects.filter(email='raskrutka89@gmail.com')

        # for user in expiring_users:
        #     self.stdout.write(f"Checking user: {user.slug}")
        #     payment_last = Payment.objects.filter(user_id=user.id, status='success', data__contains='subscriptionId').order_by('created_at').last()
        #     if payment_last:
        #
        #         payment_data = {}
        #         product = PRODUCTS.get(payment_last.product_code)
        #         order_id = uuid4().hex
        #
        #         payment = Payment.create(
        #             reference=order_id,
        #             user=user,
        #             product=product,
        #             data=payment_data,
        #         )
        #         pay_service = UnitpayService()
        #         invoice = pay_service.create_payment_subscribed(product, user, order_id)
        expiring_users = User.objects.filter(email='dev@dev.dev')
        for user in expiring_users:
            product = PRODUCTS.get('club12_tested_recurrent')
            cash = [{
                "name": "Сорокин.Клуб",
                "count": 1,
                "price": product["amount"],
                "type": "commodity",
            }]
            cash_items = b64encode(json.dumps(cash).encode())
            params = {
                "paymentType": "card",
                "account": 'f26401e13a224b5a96408c267491c7e0',
                "sum": str(product["amount"]),
                "projectId": 439242,
                "resultUrl": 'https://sorokin.club',
                "customerEmail": 'raskrutka89@gmail.com',
                "currency": "RUB",
                "subscriptionId": 5521639,
                "desc": "Сорокин.Клуб",
                "ip": socket.gethostbyname(socket.gethostname()),
                "secretKey": '7613f08591c81fe10b28595e84b3963d',
                "cashItems": b64encode(json.dumps(cash).encode()),
            }
            params["signature"] = UnitpayService.make_signature(params)

            data = {
                "paymentType": "card",
                "account": 'f26401e13a224b5a96408c267491c7e0',
                "sum": str(product["amount"]),
                "projectId": 439242,
                "resultUrl": 'https://sorokin.club',
                "customerEmail": 'raskrutka89@gmail.com',
                "currency": "RUB",
                "subscriptionId": 5521639,
                "desc": "Сорокин.Клуб",
                "ip": socket.gethostbyname(socket.gethostname()),
                "secretKey": '7613f08591c81fe10b28595e84b3963d',
                "cashItems": cash_items,
                "signature": UnitpayService.make_signature(params)
            }
            # response = requests.post(
            #     'https://unitpay.ru/api',
            #     headers={"Content-Type": "application/json"},
            #     json=data,
            # )
            requestUrl = 'https://unitpay.ru/api?method=initPayment&' + quote(self.insertUrlEncode('params', params))
            pprint(requestUrl)
            response = urlopen(requestUrl)
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
