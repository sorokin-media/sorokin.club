import logging
from datetime import datetime
from json import dumps

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import render

from notifications.email.users import send_payed_email
from payments.models import Payment
from payments.products import PRODUCTS
from payments.products import club_subscription_activator
from payments.products import club_invite_activator
from payments.unitpay import UnitpayService
from users.models.user import User
from users.models.subscription_plan import SubscriptionPlan
from notifications.telegram.common import Chat, send_telegram_message, ADMIN_CHAT

log = logging.getLogger(__name__)


def unitpay_pay(request):
    product_code = request.GET.get("product_code")
    is_invite = request.GET.get("is_invite")
    is_recurrent = request.GET.get("is_recurrent")

    # find product by code

    product = SubscriptionPlan.objects.filter(code=product_code).last()
    if not product:
        return render(request, "error.html", {
            "title": "Что-то пошло не так 😣",
            "message": "Мы не поняли, что вы хотите купить или насколько пополнить свою карту. <br/><br/>"
        })

    payment_data = {}
    now = datetime.utcnow()

    # parse email
    email = request.GET.get("email") or ""
    if email:
        email = email.lower()

    # who's paying?
    if not request.me:  # scenario 1: new user
        if not email or "@" not in email:
            return render(request, "error.html", {
                "title": "Плохой e-mail адрес 😣",
                "message": "Нам ведь нужно будет как-то привязать аккаунт к платежу"
            })

        user, _ = User.objects.get_or_create(
            email=email,
            defaults=dict(
                membership_platform_type=User.MEMBERSHIP_PLATFORM_DIRECT,
                full_name=email[:email.find("@")],
                membership_started_at=now,
                membership_expires_at=now,
                created_at=now,
                updated_at=now,
                moderation_status=User.MODERATION_STATUS_INTRO,
            ),
        )
        if request != '':
            cookie_auth = request.COOKIES.get('authUtmCookie')
            if cookie_auth:
                text_send = 'До интро ' + user.email + "\n" + cookie_auth.replace('/', "\n")
                send_telegram_message(
                    chat=Chat(id=204349098),
                    text=text_send
                )
                send_telegram_message(
                    chat=ADMIN_CHAT,
                    text=text_send
                )
    elif is_invite:  # scenario 2: invite a friend
        if not email or "@" not in email:
            return render(request, "error.html", {
                "title": "Плохой e-mail адрес друга 😣",
                "message": "Нам ведь нужно будет куда-то выслать инвайт"
            })

        friend, is_created = User.objects.get_or_create(
            email=email,
            defaults=dict(
                membership_platform_type=User.MEMBERSHIP_PLATFORM_DIRECT,
                full_name=email[:email.find("@")],
                membership_started_at=now,
                membership_expires_at=now,
                created_at=now,
                updated_at=now,
                moderation_status=User.MODERATION_STATUS_INTRO,
            ),
        )

        if not is_created:
            return render(request, "error.html", {
                "title": "Пользователь уже существует ✋",
                "message": "Юзер с таким имейлом уже есть в Клубе, "
                           "нельзя высылать ему инвайт еще раз, может он правда не хочет."
            })

        user = request.me
        payment_data = {
            "invite": email
        }
    else:  # scenario 3: account renewal
        user = request.me

    # create stripe session and payment (to keep track of history)
    pay_service = UnitpayService()
    invoice = pay_service.create_payment(product, user, is_recurrent)

    payment = Payment.create(
        reference=invoice.id,
        user=user,
        product=product,
        data=payment_data,
    )

    return render(request, "payments/pay.html", {
        "invoice": invoice,
        "product": product,
        "payment": payment,
        "user": user,
    })


def unitpay_webhook(request):
    log.info("Unitpay webhook, GET %r", request.GET)

    signature_is_valid = UnitpayService.verify_webhook(request)
    if not signature_is_valid:
        return HttpResponse(dumps({"error": {"message": "Ошибка в подписи"}}), status_code=400)

    # process payment
    order_id = request.GET["params[account]"]

    if order_id == "test":
        return HttpResponse(dumps({"result": {"message": "Тестовый запрос успешно обработан"}}))

    if request.GET["method"] == "check":
        payment = Payment.get(order_id)
        if not payment:
            return HttpResponseNotFound(dumps({"result": {"message": "Платеж не найден"}}))
        if payment.status == Payment.STATUS_STARTED:
            return HttpResponse(dumps({"result": {"message": "Проверка пройдена успешно"}}))
        return HttpResponseBadRequest(dumps({"result": {"message": "Платеж уже оплачен"}}))

    if request.GET["method"] == "pay":
        payload = request.GET
        log.info("Unitpay order %s", order_id)

        payment = Payment.finish(
            reference=order_id,
            status=Payment.STATUS_SUCCESS,
            data=payload,
        )

        if "params[subscriptionId]" in request.GET:
            user_model = payment.user
            user_model.unitpay_id = str(request.GET["params[subscriptionId]"])
            user_model.save()

        product = SubscriptionPlan.objects.filter(code=payment.product_code).last()
        if product.code == 'club1_invite':
            club_invite_activator(product, payment, payment.user)
        else:
            club_subscription_activator(product, payment, payment.user)

        if payment.user.moderation_status != User.MODERATION_STATUS_APPROVED:
            send_payed_email(payment.user)

        return HttpResponse(dumps({"result": {"message": "Запрос успешно обработан"}}))

    HttpResponseBadRequest(dumps({"result": {"message": "Неизвестный параметр method"}}))
