import json
from uuid import uuid4

from django.db import models

from payments.exceptions import PaymentNotFound, PaymentAlreadyFinalized
from users.models.user import User
from users.models.subscription_plan import SubscriptionPlan


class Payment(models.Model):
    STATUS_STARTED = "started"
    STATUS_FAILED = "failed"
    STATUS_SUCCESS = "success"
    STATUSES = [
        (STATUS_STARTED, STATUS_STARTED),
        (STATUS_FAILED, STATUS_FAILED),
        (STATUS_SUCCESS, STATUS_SUCCESS),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    reference = models.CharField(max_length=256, db_index=True)
    user = models.ForeignKey(User, related_name="payments", null=True, on_delete=models.SET_NULL, db_index=True)
    product_code = models.CharField(max_length=64)

    created_at = models.DateTimeField(auto_now_add=True)

    amount = models.FloatField(default=0.0)
    status = models.CharField(choices=STATUSES, default=STATUS_STARTED, max_length=32)
    data = models.TextField(null=True)

    class Meta:
        db_table = "payments"

    @classmethod
    def create(cls, reference: str, user: User, product: SubscriptionPlan, data: dict = None, status: str = STATUS_STARTED):
        return Payment.objects.create(
            reference=reference,
            user=user,
            product_code=product.code,
            amount=product.amount or 0.0,
            status=status,
            data=json.dumps(data),
        )

    @classmethod
    def get(cls, reference):
        return Payment.objects.filter(reference=reference).first()

    @classmethod
    def finish(cls, reference, status=STATUS_SUCCESS, data=None):
        payment = Payment.get(reference)
        # it's better to comment for tests: next 4 rows
        if not payment:
            raise PaymentNotFound()

        payment.status = status
        if data:
            payment_old_json = json.loads(payment.data)
            payment_old_json.update(data)
            payment.data = json.dumps(payment_old_json)
        payment.save()

        return payment

    @classmethod
    def for_user(cls, user):
        return Payment.objects.filter(user=user)

    def invited_user_email(self):
        # this is hacky, need to use a proper JSON field here
        if self.data:
            try:
                payment_data = json.loads(self.data)
                return payment_data.get("metadata", {}).get("invite") or payment_data.get("invite")
            except (KeyError, AttributeError):
                return None
        return None


class PaymentLink(models.Model):
    STATUS_STARTED = "started"
    STATUS_FAILED = "failed"
    STATUS_SUCCESS = "success"
    STATUS_GIVEN_TO_USER = "given_to_user"
    STATUSES = [
        (STATUS_STARTED, STATUS_STARTED),
        (STATUS_FAILED, STATUS_FAILED),
        (STATUS_SUCCESS, STATUS_SUCCESS),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    reference = models.CharField(max_length=256, db_index=True)

    email = models.EmailField(unique=False, null=True)

    title = models.TextField(null=False)
    description = models.TextField(null=False)
    amount = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    unitpay_id = models.CharField(max_length=128, null=True)

    status = models.CharField(choices=STATUSES, default=STATUS_STARTED, max_length=32)
    data = models.TextField(null=True)

    class Meta:
            db_table = "payments_link"

    @classmethod
    def create(cls, title: str, description: str,  amount: int):
        order_id = uuid4().hex
        return PaymentLink.objects.create(
            reference=order_id,
            title=title,
            description=description,
            amount=amount,
            status=PaymentLink.STATUS_STARTED,
        )

    @classmethod
    def get(cls, id):
        return PaymentLink.objects.filter(id=id).first()

    @classmethod
    def get_reference(cls, reference):
        return PaymentLink.objects.filter(reference=reference).first()

    @classmethod
    def finish(cls, reference, status=STATUS_SUCCESS, data=None):

        payment = PaymentLink.get_reference(reference)

        payment.status = status
        if data:
            if payment.data:
                payment_old_json = json.loads(payment.data)
                payment_old_json.update(data)
            else:
                payment_old_json = data
            payment.data = json.dumps(payment_old_json)
        payment.save()

        return payment
