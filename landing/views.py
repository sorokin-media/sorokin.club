import os
from datetime import datetime, timedelta

from django.conf import settings
from django.core.cache import cache
from django.db.models import Count
from django.http import Http404
from django.shortcuts import render, redirect

from auth.helpers import auth_required
from club.exceptions import AccessDenied
from landing.forms import GodmodeNetworkSettingsEditForm, GodmodeDigestEditForm, GodmodeInviteForm
from landing.models import GodSettings
from notifications.email.invites import send_invited_email
from users.models.user import User
from users.models.affilate_models import AffilateVisit

EXISTING_DOCS = [
    os.path.splitext(f)[0]  # get only filenames
    for f in os.listdir(os.path.join(settings.BASE_DIR, "frontend/html/docs"))
    if f.endswith(".html")
]


def landing(request):
    stats = cache.get("landing_stats")
    if not stats:
        stats = {
            "users": User.registered_members().count(),
            "countries": User.registered_members().values("country")
            .annotate(total=Count("country")).order_by().count() + 1,
        }
        cache.set("landing_stats", stats, settings.LANDING_CACHE_TIMEOUT)

    custom_description = 'Закрытое бизнес сообщество предпринимателей Сорокин клуб: '\
                         'мы помогаем бизнесменам становиться богаче'\
                         ' 💰онлайн нетворкинг 💰офлайн встречи 💰наставничество 💰реальный опыт от профессионалов рынка'

    if not request.me:

        identify_string = None

        if 'p' in request.GET.keys():
            # getlist instead of keys() because of exception of dublicated ?p= in URL

            p_value = request.GET.getlist('p')[0]

        else:

            p_value = None

        if 'affilate_p' in request.COOKIES.keys() and not p_value:

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
    else:
        cookie = None

    if cookie:

        return_ = render(
            request,
            "landing.html",
            {
                "stats": stats,
                'custom_description': custom_description
            }
        )
        expires = datetime.now() + timedelta(days=3650)
        return_.set_cookie('affilate_p', cookie, expires=expires)
        return return_

    return render(request, "landing.html", {
        "stats": stats,
        'custom_description': custom_description
    })

def club(request):
    stats = cache.get("landing_stats")
    if not stats:
        stats = {
            "users": User.registered_members().count(),
            "countries": User.registered_members().values("country")
            .annotate(total=Count("country")).order_by().count() + 1,
        }
        cache.set("landing_stats", stats, settings.LANDING_CACHE_TIMEOUT)

    return render(request, "pages/club.html", {
        "stats": stats
    })

def tg_bot(request):
    return render(request, "pages/tg-bot.html")

def tg_bot_second(request):
    return render(request, "pages/tg-bot-second.html")

def tg_bot_second_2(request):
    return render(request, "pages/tg-bot-second_2.html")

# Geo targeting pages

def geo_moscow(request):
    stats = cache.get("landing_stats")
    if not stats:
        stats = {
            "users": User.registered_members().count(),
            "countries": User.registered_members().values("country")
            .annotate(total=Count("country")).order_by().count() + 1,
        }
        cache.set("landing_stats", stats, settings.LANDING_CACHE_TIMEOUT)

    return render(request, "geo/moscow.html", {
        "stats": stats
    })

# ===================

def docs(request, doc_slug):
    if doc_slug not in EXISTING_DOCS:
        raise Http404()

    descriptions_and_titles = {
        'about': {
            'title': 'О клубе — правила сообщества',
            'description': 'Правила участия в Сорокин Клуб'
        },
        'contact': {
            'title': 'Контакты',
            'description': 'Связь и контакты клуба по различным вопросам'
        },
        'subscription': {
            'title': 'Правила подписки',
            'description': 'Перечень правил подписки'
        },
        'policy': {
            'title': 'Политика оплаты, доставки и возврата',
            'description': 'Клубная политика оплаты, доставки и возврата'
        }
    }
    # quiec fix bug. ehere is e.g. privacy_policy page
    try:
        custom_title = descriptions_and_titles[doc_slug]['title']
        custom_description = descriptions_and_titles[doc_slug]['description']
    except:
        custom_description = None
        custom_title = None

    return render(request, f"docs/{doc_slug}.html", {
        'custom_description': custom_description,
        'custom_title': custom_title
    })


@auth_required
def godmode_settings(request):
    if not request.me.is_god:
        raise AccessDenied()

    return render(request, "admin/godmode.html")


@auth_required
def godmode_network_settings(request):
    if not request.me.is_god:
        raise AccessDenied()

    god_settings = GodSettings.objects.first()

    if request.method == "POST":
        form = GodmodeNetworkSettingsEditForm(request.POST, request.FILES, instance=god_settings)
        if form.is_valid():
            form.save()
            return redirect("godmode_settings")
    else:
        form = GodmodeNetworkSettingsEditForm(instance=god_settings)

    return render(request, "admin/simple_form.html", {"form": form})


@auth_required
def godmode_digest_settings(request):
    if not request.me.is_god:
        raise AccessDenied()

    god_settings = GodSettings.objects.first()

    if request.method == "POST":
        form = GodmodeDigestEditForm(request.POST, request.FILES, instance=god_settings)
        if form.is_valid():
            form.save()
            return redirect("godmode_settings")
    else:
        form = GodmodeDigestEditForm(instance=god_settings)

    return render(request, "admin/simple_form.html", {"form": form})


@auth_required
def godmode_invite(request):
    if not request.me.is_god:
        raise AccessDenied()

    if request.method == "POST":
        form = GodmodeInviteForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data["email"]
            days = form.cleaned_data["days"]
            now = datetime.utcnow()
            user, is_created = User.objects.get_or_create(
                email=email,
                defaults=dict(
                    membership_platform_type=User.MEMBERSHIP_PLATFORM_DIRECT,
                    full_name=email[:email.find("@")],
                    membership_started_at=now,
                    membership_expires_at=now + timedelta(days=days),
                    created_at=now,
                    updated_at=now,
                    moderation_status=User.MODERATION_STATUS_INTRO,
                ),
            )
            send_invited_email(request.me, user)
            return render(request, "message.html", {
                "title": "🎁 Юзер приглашен",
                "message": f"Сейчас он получит на почту '{email}' уведомление об этом. "
                           f"Ему будет нужно залогиниться по этой почте и заполнить интро."
            })
    else:
        form = GodmodeInviteForm()

    return render(request, "admin/simple_form.html", {"form": form})
