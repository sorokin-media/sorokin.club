import json
from django.shortcuts import redirect, render
from django_q.tasks import async_task

from datetime import datetime, timedelta
import pytz

import decimal

from notifications.telegram.common import Chat, send_telegram_message, ADMIN_CHAT
from payments.models import Payment
from auth.helpers import auth_required, check_user_permissions
from notifications.telegram.users import notify_profile_needs_review
from posts.models.post import Post
from users.forms.intro import UserIntroForm
from users.models.geo import Geo
from users.models.user import User
from posts.models.subscriptions import PostSubscription
from pprint import pprint

from users.models.affilate_models import AffilateLogs, AffilateInfo, AffilateVisit, AffilateRelation

def bonus_to_creator(creator_user, new_one):

    time_zone = pytz.UTC
    now = time_zone.localize(datetime.utcnow())

    fee_type = AffilateInfo.objects.get(user_id=creator_user).fee_type
    percent = AffilateInfo.objects.get(user_id=creator_user).percent * 0.01

    if fee_type == 'DAYS' or fee_type == 'Дни':

        now = time_zone.localize(datetime.utcnow())
        membership_expires_at = time_zone.localize(new_one.affilated_user.membership_expires_at)

        days_on_balance = (membership_expires_at - now).days

        bonus_days = days_on_balance * percent
        bonus_days = int(decimal.Decimal(bonus_days).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_CEILING))
        membership_expires = time_zone.localize(
            new_one.creator_id.membership_expires_at + timedelta(days=bonus_days)
        )
        creator_user.membership_expires_at = membership_expires
        creator_user.save()

        new_log = AffilateLogs()
        new_log.creator_id = creator_user
        new_log.affilated_user = new_one.affilated_user
        new_log.creator_fee_type = fee_type
        new_log.percent_log = percent
        new_log.comment = f'User {creator_user.slug} get {bonus_days} days by referal programm '\
            f'from user {new_one.affilated_user.slug}. '
        new_log.bonus_amount = bonus_days
        new_log.save()

        print(f'\n\nNEW_LOG: {new_log}\n\n')

    if fee_type == 'MONEY' or fee_type == 'Деньги':

        paid_money = Payment.objects.filter(user=new_one.affilated_user).filter(
            status='success').latest('created_at').amount
        bonus_money = paid_money * percent
        bonus_money = decimal.Decimal(bonus_money).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_CEILING)

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

        # code bellow is for affilate programm
        if 'affilate_p' in request.COOKIES.keys():

            code = request.COOKIES.get('affilate_p')
            db_row_visit = AffilateVisit.objects.get(code=code)
            creator = db_row_visit.creator_id
            db_row_info = AffilateInfo.objects.get(user_id=creator)

            if db_row_visit.affilate_status == 'user visited site':

                time_zone = pytz.UTC
                now = time_zone.localize(datetime.utcnow())

                db_row_visit.affilate_status = 'come to intro'
                db_row_visit.last_page_view_time = now
                db_row_visit.save()

                new_one = AffilateRelation()
                new_one.code = db_row_visit
                new_one.creator_id = creator
                new_one.affilated_user = user
                new_one.percent = db_row_info.percent
                new_one.fee_type = db_row_info.fee_type
                new_one.save()

                bonus_to_creator(
                    creator_user=creator,
                    new_one=new_one
                )

    return render(request, "users/intro.html", {"form": form})


'''
1. записываем в афилейтвизит, что всё ок
2. записываем связь между создаталем и примкнувшим к рядам клуба


'''
