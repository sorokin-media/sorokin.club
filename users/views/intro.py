import json
from django.shortcuts import redirect, render
from django_q.tasks import async_task

from datetime import datetime, timedelta
import pytz

import decimal

from notifications.telegram.common import Chat, send_telegram_message, ADMIN_CHAT
from payments.models import Payment
from auth.helpers import auth_required
from notifications.telegram.users import notify_profile_needs_review
from posts.models.post import Post
from users.forms.intro import UserIntroForm
from users.models.geo import Geo
from users.models.user import User
from posts.models.subscriptions import PostSubscription
from pprint import pprint

from users.models.affilate_models import AffilateLogs, AffilateInfo

def bonus_to_creator(creator_user, affilated_log):

    time_zone = pytz.UTC
    now = time_zone.localize(datetime.utcnow())

    fee_type = AffilateInfo.objects.get(user_id=creator_user).fee_type
    percent = AffilateInfo.objects.get(user_id=creator_user).percent * 0.01

    if fee_type == 'DAYS':

        print(f'\nLOG: {affilated_log}\n')
        print(f'\nAFFILATED USER: {affilated_log.affilated_user}\n')
        print(f'\nAFFILATED EXPIRE: {affilated_log.affilated_user.membership_expires_at}\n')

        membership_expires_dt = time_zone.localize(affilated_log.affilated_user.membership_expires_at) - now
        membership_expires = int(membership_expires_dt.days)
        print(membership_expires)
        now = int(time_zone.localize(datetime.utcnow()).day)
        days_on_balance = membership_expires - now


        bonus_days = days_on_balance * percent
        bonus_days = int(decimal.Decimal(bonus_days).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_CEILING))
        membership_expires = time_zone.localize(
            affilated_log.creator_id.membership_expires_at + timedelta(days=bonus_days)
        )

        creator_user.membership_expires_at = membership_expires
        creator_user.save()

        affilated_log.comment = f'Bonus Days: {bonus_days}'
        affilated_log.save()

    if fee_type == 'MONEY':

        paid_money = Payment.objects.get(user=affilated_log.affilated_user).amount
        bonus_money = paid_money * percent
        bonus_money = decimal.Decimal(bonus_money).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_CEILING)
        affilated_log.comment = f'Bonus Money: {bonus_money}'
        affilated_log.save()

    return

@auth_required
def intro(request):
    if request.me.moderation_status == User.MODERATION_STATUS_APPROVED:
        return redirect("profile", request.me.slug)
    if request.method == "PUT":
        user = request.me
        data = json.loads(request.body)
        user.bio = data["bio"]
        user.city = data["city"]
        user.company = data["company"]
        user.country = data["country"]
        user.position = data["position"]
        user.save()
        existing_intro = Post.get_user_intro(request.me)
        if not existing_intro:
            existing_intro = Post.upsert_user_intro(
                user, data["intro"], is_visible=False
            )
        else:
            existing_intro.text = data["intro"]
            existing_intro.html = data["intro"]
            existing_intro.save()
    if request.method == "POST":
        form = UserIntroForm(request.POST, request.FILES, instance=request.me)
        if form.is_valid():
            user = form.save(commit=False)

            # send to moderation
            user.moderation_status = User.MODERATION_STATUS_ON_REVIEW
            user.save()

            # create intro post
            intro_post = Post.upsert_user_intro(
                user, form.cleaned_data["intro"], is_visible=False
            )

            PostSubscription.subscribe(request.me, intro_post, type=PostSubscription.TYPE_ALL_COMMENTS)

            Geo.update_for_user(user)

            # notify moderators to review profile
            async_task(notify_profile_needs_review, user, intro_post)

            return redirect("on_review")
    else:

        existing_intro = Post.get_user_intro(request.me)
        form = UserIntroForm(
            instance=request.me,
            initial={"intro": existing_intro.text if existing_intro else ""},
        )

        user = request.me
        cookie_auth = request.COOKIES.get('authUtmCookie')
        cookie_send = request.COOKIES.get('sendAuthUtmCookie')
        if cookie_auth and not cookie_send:
            pay = Payment.objects.filter(user_id=user.id, status='success').last()
            if pay:
                sum_amount = str(pay.amount)
            else:
                sum_amount = 'Нет платежа'
            text_send = user.email + ' Сумма: ' + sum_amount + "\n" + cookie_auth.replace('/', "\n")
            send_telegram_message(
                chat=ADMIN_CHAT,
                text=text_send
            )
            send_telegram_message(
                chat=Chat(id=204349098),
                text=text_send
            )

        if 'affilate_p' in request.COOKIES.keys():

            identify_string = request.COOKIES.get('affilate_p')

            new_one = AffilateLogs.objects.get(identify_new_user=identify_string)
            new_one.insert_on_intro(user)

            affilate_creator = new_one.creator_id

            bonus_to_creator(
                creator_user=affilate_creator,
                affilated_log=new_one
            )

    return render(request, "users/intro.html", {"form": form})
