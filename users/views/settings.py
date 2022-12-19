from datetime import datetime, timedelta

import stripe
from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect, get_object_or_404, render
from django_q.tasks import async_task

from auth.helpers import auth_required
from gdpr.archive import generate_data_archive
from gdpr.models import DataRequests
from search.models import SearchIndex
from users.forms.profile import ProfileEditForm, NotificationsEditForm
from users.models.geo import Geo
from users.models.user import User
from users.models.subscription import Subscription
from users.models.subscription_plan import SubscriptionPlan
from utils.strings import random_hash
from payments.models import Payment
import json
import time


@auth_required
def profile_settings(request, user_slug):
    if user_slug == "me":
        return redirect("profile_settings", request.me.slug, permanent=False)

    user = get_object_or_404(User, slug=user_slug)
    if user.id != request.me.id and not request.me.is_moderator:
        raise Http404()

    return render(request, "users/edit/index.html", {"user": user})


@auth_required
def edit_profile(request, user_slug):
    if user_slug == "me":
        return redirect("edit_profile", request.me.slug, permanent=False)

    user = get_object_or_404(User, slug=user_slug)
    if user.id != request.me.id and not request.me.is_moderator:
        raise Http404()

    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            SearchIndex.update_user_index(user)
            Geo.update_for_user(user)

            return redirect("profile", user.slug)
    else:
        form = ProfileEditForm(instance=user)

    return render(request, "users/edit/profile.html", {"form": form, "user": user})


@auth_required
def edit_account(request, user_slug):
    if user_slug == "me":
        return redirect("edit_account", request.me.slug, permanent=False)

    user = get_object_or_404(User, slug=user_slug)
    if user.id != request.me.id and not request.me.is_moderator:
        raise Http404()

    if request.method == "POST" and request.POST.get("regenerate"):
        user.secret_hash = random_hash(length=16)
        user.save()
        return redirect("edit_account", user.slug, permanent=False)

    return render(request, "users/edit/account.html", {"user": user})


@auth_required
def edit_notifications(request, user_slug):
    if user_slug == "me":
        return redirect("edit_notifications", request.me.slug, permanent=False)

    user = get_object_or_404(User, slug=user_slug)
    if user.id != request.me.id and not request.me.is_moderator:
        raise Http404()

    if request.method == "POST":
        form = NotificationsEditForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            return redirect("profile", user.slug)
    else:
        form = NotificationsEditForm(instance=user)

    return render(request, "users/edit/notifications.html", {"form": form, "user": user})


@auth_required
def edit_payments(request, user_slug):
    if user_slug == "me":
        return redirect("edit_payments", request.me.slug, permanent=False)

    user = get_object_or_404(User, slug=user_slug)
    if user.id != request.me.id and not request.me.is_moderator:
        raise Http404()

    top_users = User.objects\
        .filter(
            moderation_status=User.MODERATION_STATUS_APPROVED,
            membership_expires_at__gte=datetime.utcnow() + timedelta(days=70)
        )\
        .order_by("-membership_expires_at")[:64]

    subscriptions = []
    if user.unitpay_id:
        payment_last = Payment.objects.filter(user_id=user.id, status='success', data__contains='subscriptionId').order_by('created_at').last()
        payment_json = json.loads(payment_last.data)
        subscriptions = [dict(
            id='asdsadad',
            next_charge_at=datetime.date(user.membership_expires_at - timedelta(days=5)),
            amount=payment_last.amount,
            purse=payment_json['params[purse]']
        )]
        plan_query = SubscriptionPlan.objects.filter(code=payment_last.product_code).last()
        if plan_query:
            plans = SubscriptionPlan.objects.filter(subscription_id=plan_query.subscription_id).order_by("created_at")
        else:
            plan_subcription = Subscription.objects.filter(default=True).last()
            plans = SubscriptionPlan.objects.filter(subscription_id=plan_subcription.id).order_by("created_at")
    else:
        plan_subcription = Subscription.objects.filter(default=True).last()
        plans = SubscriptionPlan.objects.filter(subscription_id=plan_subcription.id).order_by("created_at")

    # if user.telegram_id == '204349098':
    #     plan_subcription = Subscription.objects.filter(name='Test').last()
    #     plans = SubscriptionPlan.objects.filter(subscription_id=plan_subcription.id)

    return render(request, "users/edit/payments.html", {
        "user": user,
        "subscriptions": subscriptions,
        "top_users": top_users,
        "plans": plans
    })

@auth_required
def edit_bot(request, user_slug):
    if user_slug == "me":
        return redirect("edit_bot", request.me.slug, permanent=False)

    user = get_object_or_404(User, slug=user_slug)
    if user.id != request.me.id and not request.me.is_moderator:
        raise Http404()

    return render(request, "users/edit/bot.html", {"user": user})


@auth_required
def edit_data(request, user_slug):
    if user_slug == "me":
        return redirect("edit_data", request.me.slug, permanent=False)

    user = get_object_or_404(User, slug=user_slug)
    if user.id != request.me.id and not request.me.is_god:
        raise Http404()

    return render(request, "users/edit/data.html", {"user": user})


@auth_required
def request_data(request, user_slug):
    if request.method != "POST":
        return redirect("edit_data", user_slug, permanent=False)

    user = get_object_or_404(User, slug=user_slug)
    if user.id != request.me.id and not request.me.is_god:
        raise Http404()

    DataRequests.register_archive_request(user)

    if settings.DEBUG:
        generate_data_archive(user)
    else:
        async_task(generate_data_archive, user=user)

    return render(request, "users/messages/data_requested.html")
