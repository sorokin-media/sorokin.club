import hashlib
import json
import logging
from base64 import b64encode
from dataclasses import dataclass
from urllib.parse import urlencode
from uuid import uuid4
from users.models.subscription_plan import SubscriptionPlan
from payments.models import PaymentLink

from django.conf import settings

from users.models.user import User

log = logging.getLogger(__name__)


@dataclass
class Invoice:
    id: str
    url: str


class UnitpayService:
    @classmethod
    def create_payment(cls, product: SubscriptionPlan, user: User, reccurent: bool) -> Invoice:
        order_id = uuid4().hex

        cash = [{
            "name": "Сорокин.Клуб",
            "count": 1,
            "price": product.amount,
            "type": "commodity",
        }]
        if reccurent:
            params = {
                "sum": str(product.amount),
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
                "sum": str(product.amount),
                "account": order_id,
                "desc": "Сорокин.Клуб",
                "currency": "RUB",
                "backUrl": settings.APP_HOST,
                "customerEmail": user.email,
                "cashItems": b64encode(json.dumps(cash).encode()),
            }

        params["signature"] = cls.make_signature(params)
        # for tests it's better to comment
        # and uncoment next string after
        url = "https://unitpay.ru/pay/" + settings.UNITPAY_PUBLIC_KEY + "?" + urlencode(params)
#        url = 'url'

        invoice = Invoice(
            id=order_id,
            url=url,
        )
        log.info("Created %s", invoice)

        return invoice

    @classmethod
    def create_payment_single(cls, product: PaymentLink, email: str, reccurent: bool) -> Invoice:
        cash = [{
            "name": "Сорокин.Клуб",
            "count": 1,
            "price": product.amount,
            "type": "commodity",
        }]
        if reccurent:
            params = {
                "sum": str(product.amount),
                "account": PaymentLink.reference,
                "desc": "Сорокин.Клуб",
                "currency": "RUB",
                "backUrl": settings.APP_HOST,
                "subscription": True,
                "customerEmail": email,
                "cashItems": b64encode(json.dumps(cash).encode()),
            }
        else:
            params = {
                "sum": str(product.amount),
                "account": PaymentLink.reference,
                "desc": "Сорокин.Клуб",
                "currency": "RUB",
                "backUrl": settings.APP_HOST,
                "customerEmail": email,
                "cashItems": b64encode(json.dumps(cash).encode()),
            }

        params["signature"] = cls.make_signature(params)
        # for tests it's better to comment
        # and uncoment next string after
        url = "https://unitpay.ru/pay/" + settings.UNITPAY_PUBLIC_KEY + "?" + urlencode(params)
        #        url = 'url'

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
