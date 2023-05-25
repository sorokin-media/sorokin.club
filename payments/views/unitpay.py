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

# imports for affilate programm
from users.models.affilate_models import AffilateRelation, AffilateVisit, AffilateInfo, AffilateLogs
from datetime import datetime, timedelta
import pytz
import math
import decimal

log = logging.getLogger(__name__)


def bonus_to_creator(creator_user, new_one, product):

    time_zone = pytz.UTC
    now = time_zone.localize(datetime.utcnow())

    fee_type = AffilateInfo.objects.get(user_id=creator_user).fee_type
    percent = AffilateInfo.objects.get(user_id=creator_user).percent * 0.01

    if fee_type == 'DAYS' or fee_type == 'Дни':

        # round up: 4,5 ---> 5 or 2,3 ---> 2
        bonus_day = math.ceil(product.timedelta * percent)
        creator_user.membership_expires_at = time_zone.localize(
            creator_user.membership_expires_at + timedelta(days=bonus_day)
        )
        creator_user.save()

        new_log = AffilateLogs()
        new_log.creator_id = creator_user
        new_log.affilated_user = new_one.affilated_user
        new_log.creator_fee_type = fee_type
        new_log.percent_log = percent
        new_log.comment = f'User {creator_user.slug} get {bonus_day} days by referal programm '\
            f'from user {new_one.affilated_user.slug}. '
        new_log.bonus_amount = bonus_day
        new_log.save()

    if fee_type == 'MONEY' or fee_type == 'Деньги':

        paid_money = product.amount
        bonus_money = paid_money * percent
        bonus_money = decimal.Decimal(bonus_money).quantize(decimal.Decimal('0.1'), rounding=decimal.ROUND_CEILING)

        new_log = AffilateLogs()
        new_log.creator_id = creator_user
        new_log.affilated_user = new_one.affilated_user
        new_log.creator_fee_type = fee_type
        new_log.percent_log = percent
        new_log.comment = f'User {creator_user.slug} get {bonus_money} money by referal programm'\
            f'from user {new_one.affilated_user.slug}. '
        new_log.bonus_amount = bonus_money
        new_log.save()

        aff_info_obj = AffilateInfo.objects.get(user_id=creator_user)
        aff_info_obj.sum += bonus_money
        aff_info_obj.save()

    return


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
        # code about referral programm
        if 'affilate_p' in request.COOKIES.keys():

            code = request.COOKIES.get('affilate_p')
            db_row_visit = AffilateVisit.objects.filter(code=code).first()
            creator = db_row_visit.creator_id

            if not AffilateRelation.objects.filter(creator_id=creator).filter(affilated_user=user).exists():

                db_row_info = AffilateInfo.objects.get(user_id=creator)
                new_one = AffilateRelation()
                new_one.creator_id = creator
                new_one.affilated_user = user
                new_one.percent = db_row_info.percent
                new_one.fee_type = db_row_info.fee_type
                new_one.last_product = product
                new_one.save()

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
    identify_string = None
    if 'p' in request.GET.keys():
        # getlist instead of keys() because of exception of dublicated ?p= in URL

        p_value = request.GET.getlist('p')[0]
        identify_string = None

    else:

        p_value = None

    if 'affilate_p' in request.COOKIES.keys():

        identify_string = request.COOKIES.get('affilate_p')

    new_one = AffilateVisit()
    done = new_one.insert_first_time(
        p_value=p_value,
        code=identify_string,
        url=request.build_absolute_uri()
    )
    if done:
        cookie = new_one.code
    else:
        cookie = None

    # create stripe session and payment (to keep track of history)
    pay_service = UnitpayService()
    print(f'PRODUCT USER IS_RECCURECT: {product, user, is_recurrent}')
    invoice = pay_service.create_payment(product, user, is_recurrent)

    payment = Payment.create(
        reference=invoice.id,
        user=user,
        product=product,
        data=payment_data,
    )

    if cookie:

        return_ = render(
            request,
            "payments/pay.html",
            {
                "invoice": invoice,
                "product": product,
                "payment": payment,
                "user": user
            }
        )
        expires = datetime.now() + timedelta(days=3650)
        return_.set_cookie('affilate_p', cookie, expires=expires)
        return return_

    return render(request, "payments/pay.html", {
        "invoice": invoice,
        "product": product,
        "payment": payment,
        "user": user,
    })


def unitpay_webhook(request):
    log.info("Unitpay webhook, GET %r", request.GET)

    # for tests it's better to comment: next 3 rows
    signature_is_valid = UnitpayService.verify_webhook(request)
    if not signature_is_valid:
        return HttpResponse(dumps({"error": {"message": "Ошибка в подписи"}}), status_code=400)

    # process payment, get account from webhook
    order_id = request.GET["params[account]"]

    if order_id == '549269b5dd0b4ea29aaef0d117322b85':
        return HttpResponse(dumps({"result": {"message": "Запрос успешно обработан"}}))

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

        # subscriptionId -> references in DB table

        user_model = payment.user

        if "params[subscriptionId]" in request.GET:
            user_model.unitpay_id = int(request.GET["params[subscriptionId]"])
            user_model.save()

        product = SubscriptionPlan.objects.filter(code=payment.product_code).last()
        if product.code == 'club1_invite':
            club_invite_activator(product, payment, payment.user)
        else:
            club_subscription_activator(product, payment, payment.user)
        # it's better to comment for tests: next 2 rows
        if payment.user.moderation_status != User.MODERATION_STATUS_APPROVED:
            send_payed_email(payment.user)

        # if there is affilate relation where affilated user is who pay
        if AffilateRelation.objects.filter(affilated_user=user_model).exists():

            # get object of this relation

            new_one = AffilateRelation.objects.filter(affilated_user=user_model).latest('created_at')
            # plus days or money depending on setting in user's profile
            bonus_to_creator(
                creator_user=new_one.creator_id,
                new_one=new_one,
                product=product
            )

        return HttpResponse(dumps({"result": {"message": "Запрос успешно обработан"}}))

    HttpResponseBadRequest(dumps({"result": {"message": "Неизвестный параметр method"}}))
