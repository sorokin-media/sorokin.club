import random
from datetime import datetime, timedelta

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect, render, get_object_or_404

from auth.helpers import auth_required, set_session_cookie
from auth.models import Session
from club.exceptions import AccessDenied
from posts.models.post import Post
from users.models.user import User
from utils.strings import random_string
from users.models.subscription import Subscription
from users.models.subscription_plan import SubscriptionPlan
import time

from users.models.affilate_models import AffilateVisit

def join(request):
    if request.me:
        return redirect("profile", request.me.slug)
    if time.time() < 1659838399:
        cookie_sale = request.COOKIES.get('sale-november')
        get_sale = request.GET.get("sale-november")
        if cookie_sale or get_sale:
            plans = SubscriptionPlan.objects.filter(
                subscription_id='ea5d1894-fb02-4266-8083-23af90d393b0').order_by("created_at")
        else:
            plan_subcription = Subscription.objects.filter(default=True).last()
            plans = SubscriptionPlan.objects.filter(subscription_id=plan_subcription.id).order_by("created_at")
    else:
        plan_subcription = Subscription.objects.filter(default=True).last()
        plans = SubscriptionPlan.objects.filter(subscription_id=plan_subcription.id).order_by("created_at")

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

    if cookie:

        return_ = render(
            request,
            "auth/join.html",
            {
                "plans": plans
            }
        )
        expires = datetime.now() + timedelta(days=3650)
        return_.set_cookie('affilate_p', cookie, expires=expires)
        return return_

    return render(request, "auth/join.html", {
        "plans": plans
    })


def login(request):
    if request.me:
        return redirect("profile", request.me.slug)

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

    return render(request, "auth/login.html", {
        "goto": request.GET.get("goto"),
        "email": request.GET.get("email"),
    })


@auth_required
def logout(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    token = request.COOKIES.get("token")
    Session.objects.filter(token=token).delete()
    cache.delete(f"token:{token}:session")
    return redirect("index")


def debug_dev_login(request):
    if not (settings.DEBUG or settings.TESTS_RUN):
        raise AccessDenied(title="Эта фича доступна только при DEBUG=true")

    user, is_created = User.objects.get_or_create(
        slug="dev",
        defaults=dict(
            patreon_id="123456",
            membership_platform_type=User.MEMBERSHIP_PLATFORM_PATREON,
            email="dev@dev.dev",
            full_name="Senior 23 y.o. Developer",
            company="FAANG",
            position="Team Lead конечно",
            balance=10000,
            membership_started_at=datetime.utcnow(),
            membership_expires_at=datetime.utcnow() + timedelta(days=365 * 100),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_email_verified=True,
            moderation_status=User.MODERATION_STATUS_APPROVED,
            roles=["god"],
        ),
    )

    if is_created:
        Post.upsert_user_intro(user, "Очень плохое интро", is_visible=True)

    session = Session.create_for_user(user)

    return set_session_cookie(redirect("profile", user.slug), user, session)


def debug_random_login(request):
    if not (settings.DEBUG or settings.TESTS_RUN):
        raise AccessDenied(title="Эта фича доступна только при DEBUG=true")

    slug = "random_" + random_string()
    user, is_created = User.objects.get_or_create(
        slug=slug,
        defaults=dict(
            patreon_id=random_string(),
            membership_platform_type=User.MEMBERSHIP_PLATFORM_PATREON,
            email=slug + "@random.dev",
            full_name="%s %d y.o. Developer" % (random.choice(["Максим", "Олег"]), random.randint(18, 101)),
            company="Acme Corp.",
            position=random.choice(["Подниматель пингвинов", "Опускатель серверов", "Коллектор пивных бутылок"]),
            balance=10000,
            membership_started_at=datetime.utcnow(),
            membership_expires_at=datetime.utcnow() + timedelta(days=365 * 100),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_email_verified=True,
            moderation_status=User.MODERATION_STATUS_APPROVED,
        ),
    )

    if is_created:
        Post.upsert_user_intro(user, "Интро как интро, аппрув прошло :Р", is_visible=True)

    session = Session.create_for_user(user)

    return set_session_cookie(redirect("profile", user.slug), user, session)


def debug_login(request, user_slug):
    if not (settings.DEBUG or settings.TESTS_RUN):
        raise AccessDenied(title="Эта фича доступна только при DEBUG=true")

    user = get_object_or_404(User, slug=user_slug)
    session = Session.create_for_user(user)

    return set_session_cookie(redirect("profile", user.slug), user, session)
