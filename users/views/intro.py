import json
from django.shortcuts import redirect, render
from django_q.tasks import async_task

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

    return render(request, "users/intro.html", {"form": form})
