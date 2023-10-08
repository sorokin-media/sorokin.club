from django.shortcuts import get_object_or_404, render, redirect
from payments.models import PaymentLink
from payments.forms.payment_link import PaymentLinkForm
from pprint import pprint
from django.http import HttpResponse
import re
import json
from urllib.parse import quote
from base64 import b64encode
from django.conf import settings
from django.core.management import BaseCommand
from users.models.user import User
from payments.models import Payment
from notifications.email.users import send_subscribe_8_email
from notifications.email.users import couldnd_withdraw_money_email
from notifications.email.users import cancel_subscribe_user_email, payment_reminder_5_email, payment_reminder_3_email, payment_reminder_1_email
from notifications.telegram.users import subscribe_8_user
from notifications.telegram.users import couldnd_withdraw_money
from notifications.telegram.users import cancel_subscribe_user, payment_reminder_5, payment_reminder_3, payment_reminder_1, cancel_subscribe_admin
from users.models.subscription_plan import SubscriptionPlan
from payments.unitpay import UnitpayService
from urllib.request import urlopen
from urllib.parse import quote
from notifications.telegram.common import Chat, send_telegram_message, ADMIN_CHAT, render_html_message
from django.urls import reverse

def create_payment_link(request):
    if request.method == "POST":

        form = PaymentLinkForm(request.POST)
        if form.is_valid():
            PaymentLink.create(
                request.POST.get("title"),
                request.POST.get("description"),
                request.POST.get("amount"),
            )
        return redirect("/payment_link")
    else:
        form = PaymentLinkForm()
    return render(request, "payments/link/create.html", {
        "form": form
    })

def update_single_link(request, link_id):
    payment_obj = PaymentLink.objects.get(id=link_id)
    if request.method == "POST":
        payment_obj.title = request.POST.get("title")
        payment_obj.description = request.POST.get("description")
        payment_obj.amount = int(request.POST.get("amount"))
        payment_obj.save()
        return redirect("/payment_link")

    if payment_obj:
        form = PaymentLinkForm(initial={"title": payment_obj.title, "description": payment_obj.description, "amount": int(payment_obj.amount)})
    else:
        form = PaymentLinkForm()


    return render(request, "payments/link/update.html", {
        "form": form
    })

def given_to_user_link(request, link_id):
    payment_obj = PaymentLink.objects.get(id=link_id)

    payment_obj.status = PaymentLink.STATUS_GIVEN_TO_USER
    payment_obj.save()
    return redirect("/payment_link")

def get_pay_link(request, link_id):
    payment_obj = PaymentLink.objects.get(id=link_id)

    return render(request, "payments/link/view.html", {
        "payment": payment_obj
    })

def payment_link_thanks(request):
    return render(request, "payments/link/thanks.html", {
    })

def write_of_money(request, link_id):
    payment_obj = PaymentLink.objects.filter(id=link_id).last()
    if request.method == "POST":
        form = PaymentLinkForm(request.POST)
        if form.is_valid():
            payment_last = PaymentLink.objects.filter(id=link_id).last()
            if payment_last:
                product_new = PaymentLink.create(
                    request.POST.get("title"),
                    request.POST.get("description"),
                    request.POST.get("amount"),
                )
                product_new.email = payment_last.email
                product_new.unitpay_id = payment_last.unitpay_id
                product_new.save()

                payment_json = json.loads(payment_last.data)
                cash = [{
                    "name": "Sorokin.Club",
                    "count": 1,
                    "price": product_new.amount,
                    "type": "commodity",
                }]
                cash_items = quote(b64encode(json.dumps(cash).encode()))
                data = {
                    "paymentType": payment_json['params[paymentType]'][0],
                    "account": product_new.reference,
                    "sum": str(product_new.amount),
                    "projectId": 439242,
                    "resultUrl": 'https://sorokin.club',
                    "customerEmail": product_new.email,
                    "currency": "RUB",
                    "subscriptionId": product_new.unitpay_id,
                    "desc": "Sorokin.Club",
                    "ip": payment_json['params[ip]'][0],
                    "secretKey": settings.UNITPAY_SECRET_KEY,
                    "cashItems": cash_items
                }
                data["signature"] = UnitpayService.make_signature(data)

                requestUrl = 'https://unitpay.ru/api?method=initPayment&' + insertUrlEncode('params', data)
                response = urlopen(requestUrl)
                data = response.read().decode('utf-8')
                jsons = json.loads(data)
                if 'error' in jsons:
                    text_send = '#ПОВТОРНОЕ_СПИСАНИЕ_ОШИБКА ' + jsons['error']['message']
                    send_telegram_message(
                        chat=ADMIN_CHAT,
                        text=text_send
                    )
                else:
                    print("Success")
                    text_send = '#ПОВТОРНОЕ_СПИСАНИЕ ' + str(product_new.amount)
                    send_telegram_message(
                        chat=ADMIN_CHAT,
                        text=text_send
                    )
            return redirect("/payment_link")
        return redirect("/payment_link")

    if payment_obj:
        form = PaymentLinkForm(initial={"title": payment_obj.title, "description": payment_obj.description, "amount": int(payment_obj.amount)})
    else:
        form = PaymentLinkForm()


    return render(request, "payments/link/repeat.html", {
        "form": form
    })

def insertUrlEncode(inserted, params):
    result = ''
    first = True
    for p in params:
        if first:
            first = False
        else:
            result += '&'
        result += inserted + '[' + p + ']=' + str(params[p])
    return result
