import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse
from django_q.tasks import async_task

from auth.helpers import set_session_cookie
from auth.models import Session, Code
from notifications.email.users import send_auth_email, send_payed_email
from notifications.telegram.users import notify_user_auth
from users.models.user import User

log = logging.getLogger(__name__)


def email_login(request):
    if request.method != "POST":
        return redirect("login")

    goto = request.POST.get("goto")
    email_or_login = request.POST.get("email_or_login")
    if not email_or_login:
        return redirect("login")

    email_or_login = email_or_login.strip()

    if "|-" in email_or_login:
        # secret_hash login
        email_part, secret_hash_part = email_or_login.split("|-", 1)
        user = User.objects.filter(email=email_part, secret_hash=secret_hash_part).first()
        if not user:
            return render(request, "error.html", {
                "title": "Такого юзера нет 🤔",
                "message": "Пользователь с таким кодом не найден. "
                           "Попробуйте авторизоваться по обычной почте или юзернейму.",
            }, status=404)

        if user.deleted_at:
            # cancel user deletion
            user.deleted_at = None
            user.save()

        session = Session.create_for_user(user)
        redirect_to = reverse("profile", args=[user.slug]) if not goto else goto
        response = redirect(redirect_to)
        return set_session_cookie(response, user, session)
    else:
        if settings.FREE_MEMBERSHIP:
            # email login or sign up
            now = datetime.utcnow()

            try:
                log.info("Add new user %s", email_or_login)

                user, created = User.objects.get_or_create(
                    email=email_or_login.lower(),
                    defaults=dict(
                        membership_platform_type=User.MEMBERSHIP_PLATFORM_DIRECT,
                        full_name=email_or_login[:email_or_login.find("@")],
                        membership_started_at=now,
                        membership_expires_at=now,
                        created_at=now,
                        updated_at=now,
                        moderation_status=User.MODERATION_STATUS_INTRO,
                    ),
                )

                if created:
                    send_payed_email(user)

            except IntegrityError:
                return render(request, "error.html", {
                    "title": "Что-то пошло не так 🤔",
                    "message": "Напишите нам, и мы всё починим. Или попробуйте ещё раз.",
                }, status=404)
        else:
            # email/nickname login
            user = User.objects.filter(Q(email=email_or_login.lower()) | Q(slug=email_or_login)).first()
            if not user:
                return render(request, "error.html", {
                    "title": "Такого юзера нет 🤔",
                    "message": "Пользователь с такой почтой не найден в списке членов Клуба. "
                               "Попробуйте другую почту или никнейм. "
                               "Если совсем ничего не выйдет, напишите нам, попробуем помочь.",
                }, status=404)

        code = Code.create_for_user(user=user, recipient=user.email, length=settings.AUTH_CODE_LENGTH)
        async_task(send_auth_email, user, code)
        async_task(notify_user_auth, user, code)

        return render(request, "auth/email.html", {
            "email": user.email,
            "goto": goto,
            "restore": user.deleted_at is not None,
        })


def email_login_code(request):
    email = request.GET.get("email")
    code = request.GET.get("code")
    if not email or not code:
        return redirect("login")

    goto = request.GET.get("goto")
    email = email.lower().strip()
    code = code.lower().strip()

    user = Code.check_code(recipient=email, code=code)
    session = Session.create_for_user(user)

    if not user.is_email_verified:
        # save 1 click and verify email
        user.is_email_verified = True
        user.save()

    if user.deleted_at:
        # cancel user deletion
        user.deleted_at = None
        user.save()

    redirect_to = reverse("profile", args=[user.slug]) if not goto else goto
    response = redirect(redirect_to)
    return set_session_cookie(response, user, session)
