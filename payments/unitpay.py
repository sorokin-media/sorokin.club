import hashlib
import json
import logging
import socket
from base64 import b64encode
from dataclasses import dataclass
from urllib.parse import urlencode
from uuid import uuid4
import requests

from django.conf import settings

from users.models.user import User

log = logging.getLogger(__name__)


@dataclass
class Invoice:
    id: str
    url: str


class UnitpayService:
    @classmethod
    def create_payment(cls, product: dict, user: User) -> Invoice:
        order_id = uuid4().hex

        cash = [{
            "name": "Сорокин.Клуб",
            "count": 1,
            "price": product["amount"],
            "type": "commodity",
        }]
        if product["recurrent"]:
            params = {
                "sum": str(product["amount"]),
                "account": order_id,
                "desc": "Сорокин.Клуб",
                "currency": "RUB",
                "backUrl": settings.APP_HOST,
                "subscription": True,
                "customerEmail": user.email,
                "cashItems": b64encode(json.dumps(cash).encode()),
            }
        else:
            params = {
                "sum": str(product["amount"]),
                "account": order_id,
                "desc": "Сорокин.Клуб",
                "currency": "RUB",
                "backUrl": settings.APP_HOST,
                "customerEmail": user.email,
                "cashItems": b64encode(json.dumps(cash).encode()),
            }

        params["signature"] = cls.make_signature(params)

        url = "https://unitpay.ru/pay/" + settings.UNITPAY_PUBLIC_KEY + "?" + urlencode(params)

        invoice = Invoice(
            id=order_id,
            url=url,
        )
        log.info("Created %s", invoice)

        return invoice

    @classmethod
    def make_signature(cls, payload) -> str:
        fields = ("account", "currency", "desc", "sum")
        string = "{up}".join([payload[field] for field in fields] + [settings.UNITPAY_SECRET_KEY])
        signature = hashlib.sha256(string.encode()).hexdigest()
        return signature

    @classmethod
    def verify_webhook(cls, request) -> bool:
        log.info("Verify request")

        method = None
        signature = None
        params = dict()

        for k, v in request.GET.items():
            if k == "method":
                method = v

            elif k == "params[signature]":
                signature = v

            else:
                k = k.replace("params[", "").replace("]", "")
                params[k] = v

        string = "{up}".join([method] + [params[k] for k in sorted(params.keys())] + [settings.UNITPAY_SECRET_KEY])
        counted_signature = hashlib.sha256(string.encode()).hexdigest()

        return signature == counted_signature

    def create_payment_subscribed(cls, product: dict, user: User, order_id) -> Invoice:

        cash = [{
            "name": "Сорокин.Клуб",
            "count": 1,
            "price": product["amount"],
            "type": "commodity",
        }]
        params = {
            "paymentType": "card",
            "account": order_id,
            "sum": str(product["amount"]),
            "projectId": 439242,
            "resultUrl": 'https://sorokin.club',
            "customerEmail": user.email,
            "currency": "RUB",
            "subscriptionId": user.unitpay_id,
            "desc": "Сорокин.Клуб",
            "ip": socket.gethostbyname(socket.gethostname()),
            "secretKey": settings.UNITPAY_SECRET_KEY,
            "cashItems": b64encode(json.dumps(cash).encode()),
        }
        params["signature"] = cls.make_signature(params)

        response = requests.post(
            url='https://unitpay.ru/api',
            headers={"Content-Type": "application/json"},
            data={
                "method": 'initPayment',
                "params": params,
            },
        )

        return response
