from django.shortcuts import get_object_or_404, render, redirect
from payments.models import PaymentLink
from payments.forms.payment_link import PaymentLinkForm
from pprint import pprint
from django.http import HttpResponse
import re

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
