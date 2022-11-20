from datetime import timedelta, datetime
from urllib.parse import urlencode

import pytz
import datetime as DT
from django.db.models import Count, Q, Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET
from icalendar import Calendar, Event

from auth.helpers import auth_required
from badges.models import UserBadge
from landing.models import GodSettings
from users.models.achievements import Achievement
from users.models.user import User
from payments.models import Payment


@auth_required
def stats(request):
    achievements = Achievement.objects\
        .annotate(user_count=Count('users'))\
        .filter(is_visible=True)\
        .filter(user_count__gt=0)\
        .exclude(code__in=["old", "parliament_member"])\
        .order_by('-user_count')

    latest_badges = UserBadge.objects\
        .select_related("badge", "to_user")\
        .order_by('-created_at')[:20]

    top_badges = list(filter(None.__ne__, [
        User.registered_members().filter(id=to_user).first() for to_user, _ in UserBadge.objects
        .filter(created_at__gte=datetime.utcnow() - timedelta(days=150))
        .values_list("to_user")
        .annotate(sum_price=Sum("badge__price_days"))
        .order_by("-sum_price")[:7]  # select more in case someone gets deleted
    ]))[:5]  # filter None

    moderators = User.objects\
        .filter(Q(roles__contains=[User.ROLE_MODERATOR]) | Q(roles__contains=[User.ROLE_GOD]))

    parliament = User.objects.filter(achievements__achievement_id="parliament_member")

    top_users = User.objects\
        .filter(
            moderation_status=User.MODERATION_STATUS_APPROVED,
            membership_expires_at__gte=datetime.utcnow() + timedelta(days=70)
        )\
        .order_by("-membership_expires_at")[:64]

    return render(request, "pages/stats.html", {
        "achievements": achievements,
        "latest_badges": latest_badges,
        "top_badges": top_badges,
        "top_users": top_users,
        "moderators": moderators,
        "parliament": parliament,
    })

@auth_required
def stats_gode(request):
    # '2022-10-03 00:00:00' and '2022-11-06 23:59:59'
    payment_first = []
    dt = DT.datetime.strptime('2022-10-03 00:00:00', '%Y-%m-%d %H:%M:%S')
    datetime_for = dt.timestamp()
    expiring_users = User.objects.filter(moderation_status='approved')
    sum_first = 0
    count_first = 0
    for user in expiring_users:
        payment_one = Payment.objects.filter(user_id=user.id, status='success').order_by('created_at').first()
        if payment_one:
            date = str(payment_one.created_at)
            dt = DT.datetime.strptime('-'.join(date.split('.')[:-1]), '%Y-%m-%d %H:%M:%S')
            if payment_one and int(dt.timestamp()) > int(datetime_for):
                payment_first.extend([payment_one.reference,payment_one.amount,payment_one.created_at])
                sum_first += payment_one.amount
                count_first += 1

    return render(request, "pages/stats-gode.html", {
        "payment_first": payment_first,
        "sum_first": sum_first,
        "count_first": count_first,
    })


@auth_required
def network(request):
    secret_page_html = GodSettings.objects.first().network_page
    return render(request, "pages/network.html", {
        "page_html": secret_page_html,
    })


@require_GET
def robots(request):
    lines = [
        "User-agent: *",
        "Sitemap: https://sorokin.club/sitemap.xml",
        "Host: https://sorokin.club",
        "Disallow: /intro/",
        "Disallow: /user/",
        "Disallow: /people/",
        "Clean-param: comment_order&goto /",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


@auth_required
def generate_ical_invite(request):
    event_title = request.GET.get("title")
    event_date = request.GET.get("date")
    event_url = request.GET.get("url")
    event_location = request.GET.get("location")
    event_timezone = request.GET.get("timezone")

    if not event_title or not event_date or not event_timezone:
        return HttpResponse("No date, tz or title")

    event_date = datetime.fromisoformat(event_date).replace(tzinfo=pytz.timezone(event_timezone))

    cal = Calendar()
    event = Event()
    event.add("summary", event_title)
    event.add("dtstart", event_date)
    event.add("dtend", event_date + timedelta(hours=2))

    if event_url:
        event.add("description", f"{event_url}")

    if event_location:
        event.add("location", event_location)

    cal.add_component(event)

    response = HttpResponse(cal.to_ical(), content_type="application/force-download")
    response["Content-Disposition"] = "attachment; filename=ical_sorokin_club.ics"
    return response


@auth_required
def generate_google_invite(request):
    event_title = request.GET.get("title")
    event_date = request.GET.get("date")
    event_url = request.GET.get("url")
    event_location = request.GET.get("location")
    event_timezone = request.GET.get("timezone")

    if not event_title or not event_date or not event_timezone:
        return HttpResponse("No date, tz or title")

    event_date = datetime.fromisoformat(event_date)

    google_url_params = urlencode({
        "text": event_title,
        "dates": "{}/{}".format(
            event_date.strftime("%Y%m%dT%H%M%S"),
            (event_date + timedelta(hours=2)).strftime("%Y%m%dT%H%M%S"),
        ),
        "details": f"{event_url}",
        "location": event_location,
        "ctz": event_timezone,
    })

    return redirect(f"https://calendar.google.com/calendar/u/0/r/eventedit?{google_url_params}")
