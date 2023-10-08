# Python imports
import datetime as DT
import time
from datetime import datetime, timedelta
import pytz

# Django imports
from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404, render
from django.http import Http404
from django.shortcuts import render, redirect
from django.shortcuts import redirect, get_object_or_404, render
from django.http import Http404

# import models
from users.models.user import User
from users.models.random_coffee import RandomCoffee
from payments.models import Payment
from posts.models.post import Post
from comments.models import Comment
from users.models.subscription import Subscription
from users.models.subscription_plan import SubscriptionPlan
from users.models.affilate_models import AffilateLogs, AffilateRelation
from payments.models import PaymentLink

# import config data
from club.settings import APP_HOST as host

# import custom classes
from auth.helpers import auth_required
from stats.forms.money import DateForm, PaymentLinkSingleForm
from payments.forms.payment_link import PaymentLinkForm
from users.models.affilate_models import AffilateLogs

from pprint import pprint

def active_or_not(user):

    time_zone = pytz.UTC
    now = time_zone.localize(datetime.utcnow())

    x = now < time_zone.localize(user.membership_expires_at)
    y = user.is_banned_until is None
    if not y:
        y = user.is_banned_until < now
    z = user.moderation_status == 'approved'

    return "Активен" if x and y and z else "Не активен"

# Create your views here.
@auth_required
def stats_gode(request):
    # Это ублюдство надо переписать
    if request.method == "POST":

        form = DateForm(request.POST)
        date_from_string = request.POST.get('date_from') + ' 00:00:00'
        date_to_string = request.POST.get('date_to') + ' 00:00:00'
        dt = DT.datetime.strptime(date_from_string, '%Y-%m-%d %H:%M:%S')
        datetime_for = dt.timestamp()

        # быстрый костыль для бага с тем, что конечная дата не включается
        # а ублюдство действительно надо переделать, прост кошмар какой то
        date_format = '%Y-%m-%d %H:%M:%S'
        date_obj = datetime.strptime(date_to_string, date_format)
        date_plus_one_day = date_obj + timedelta(days=1)
        date_to_string = date_plus_one_day.strftime(date_format)
        # конец костыля

        property(date_to_string)
        dt = DT.datetime.strptime(date_to_string, '%Y-%m-%d %H:%M:%S')
        datetime_to = dt.timestamp()
        payment_first = []
        payment_exclude = []
        sum_first = 0
        count_first = 0
        sum_auto_payment = 0
        count_auto_payment = 0
        sum_no_auto_payment = 0
        count_no_auto_payment = 0
        expiring_users = User.objects.filter(moderation_status='approved')
        for user in expiring_users:
            payment_one = Payment.objects.filter(user_id=user.id, status='success').order_by('created_at').first()
            if payment_one:
                payment_exclude.extend([payment_one.id])
                date = str(payment_one.created_at)
                dt = DT.datetime.strptime('-'.join(date.split('.')[:-1]), '%Y-%m-%d %H:%M:%S')
                if payment_one and int(dt.timestamp()) > int(datetime_for) and int(dt.timestamp()) <= int(
                        datetime_to):
                    payment_first.extend([payment_one.reference, payment_one.amount, payment_one.created_at])
                    sum_first += payment_one.amount
                    count_first += 1

        auto_payment = Payment.objects.filter(status='success',
                                              created_at__gte=date_from_string,
                                              created_at__lte=date_to_string).exclude(data__contains='params[3ds]')
        for auto in auto_payment:
            payment_exclude.extend([auto.id])
            sum_auto_payment += auto.amount
            count_auto_payment += 1

        else_payment = Payment.objects.filter(status='success',
                                              created_at__gte=date_from_string,
                                              created_at__lte=date_to_string).exclude(id__in=payment_exclude)
        for else_p in else_payment:
            sum_no_auto_payment += else_p.amount
            count_no_auto_payment += 1
    else:
        form = DateForm
        payment_first = []
        sum_first = 0
        count_first = 0
        sum_auto_payment = 0
        count_auto_payment = 0
        sum_no_auto_payment = 0
        count_no_auto_payment = 0

    return render(request, "pages/stats-gode.html", {
        "payment_first": payment_first,
        "sum_first": sum_first,
        "count_first": count_first,
        "form": form,
        "sum_auto_payment": sum_auto_payment,
        "count_auto_payment": count_auto_payment,
        "sum_no_auto_payment": sum_no_auto_payment,
        "count_no_auto_payment": count_no_auto_payment,
    })


@auth_required
def stats_content(request):
    if request.method == "POST":
        form = DateForm(request.POST)
        date_from_string = request.POST.get('date_from') + ' 00:00:00'
        date_to_string = request.POST.get('date_to') + ' 00:00:00'

        approve_intro = Post.objects.filter(type='intro',
                                            is_approved_by_moderator=True,
                                            published_at__gte=date_from_string,
                                            published_at__lte=date_to_string).count()

        publish_post = Post.objects.filter(is_approved_by_moderator=True,
                                           published_at__gte=date_from_string,
                                           published_at__lte=date_to_string).exclude(type='intro').count()

        count_comments = Comment.objects.filter(is_deleted=False,
                                                created_at__gte=date_from_string,
                                                created_at__lte=date_to_string).count()

    else:
        form = DateForm
        approve_intro = 0
        publish_post = 0
        count_comments = 0

    return render(request, "pages/stats-content.html", {
        "approve_intro": approve_intro,
        "publish_post": publish_post,
        "count_comments": count_comments,
        "form": form,
    })


@auth_required
def stats_buddy(request):
    intro_posts = Post.objects.filter(type='intro',
                                      is_approved_by_moderator=True,
                                      buddy_counter__gte=1)

    return render(request, "pages/stats-buddy.html", {
        "buddys": intro_posts
    })


@auth_required
def edit_payments_sale(request):
    if request.me.slug == "me":
        return redirect("edit_payments", request.me.slug, permanent=False)

    user = get_object_or_404(User, slug=request.me.slug)
    if user.id != request.me.id and not request.me.is_moderator:
        raise Http404()

    subscriptions = []
    # распродажа нг
    if time.time() < 1671998399:
        plans = SubscriptionPlan.objects.filter(subscription_id='8ea7819e-d83f-448a-a3e8-41f9744cd957').order_by(
            "created_at")
    else:
        plan_subcription = Subscription.objects.filter(default=True).last()
        plans = SubscriptionPlan.objects.filter(subscription_id=plan_subcription.id).order_by("created_at")

    return render(request, "pages/payments_sale.html", {
        "user": user,
        "subscriptions": subscriptions,
        "plans": plans
    })

def rating_helper(posts):
    posts_data = []

    for post in posts:
        points = (post.upvotes*10) + (post.comment_count*3) + post.view_count
        posts_data.append({'post': post, 'points': points})
    newlist = sorted(posts_data, key=lambda post: post['points'], reverse=True)
    return newlist

@auth_required
def posts_rating(request):
    if request.method == 'POST':
        form = DateForm(request.POST)
        time_zone = pytz.UTC
        range_date = request.POST['date-range']
        range_date = range_date.replace(' ', '').replace('-', ' ')
        range_date = range_date.split()
        start_year, start_month, start_day = int(range_date[0]), int(range_date[1]), int(range_date[2])
        finish_year, finish_month, finish_day = int(range_date[3]), int(range_date[4]), int(range_date[5])
        # __range from Django ORM don't resolve task, because of doesn't include dates
        # note that there are posts without date "created_at" in DB. But that one means that post was deleted
        posts = Post.objects.filter(published_at__date__gte=time_zone.localize(
            datetime(start_year, start_month, start_day))).filter(
            published_at__date__lte=time_zone.localize(
                datetime(finish_year, finish_month, finish_day))).exclude(type='intro').all()
        newlist = rating_helper(posts)
        return render(request, "pages/posts-rating.html",
                      {"posts": newlist, "form": form})
    else:
        form = DateForm
        newlist = []
        return render(request, "pages/posts-rating.html",
                      {"posts": newlist, 'form': form})

@auth_required
def random_coffee_stat(request):
    coffee_list = RandomCoffee.objects.filter(random_coffee_is=True).all()
    return render(
        request,
        'pages/coffee-rating.html',
        {'coffee_list': coffee_list}
    )

@auth_required
def affilates_stat(request):
    return render(
        request,
        'pages/stats-affilate.html'
    )

def get_list_of_logs(request_post):

    time_zone = pytz.UTC
    range_date = request_post['date-range']
    range_date = range_date.replace(' ', '').replace('-', ' ')
    range_date = range_date.split()
    start_year, start_month, start_day = int(range_date[0]), int(range_date[1]), int(range_date[2])
    finish_year, finish_month, finish_day = int(range_date[3]), int(range_date[4]), int(range_date[5])

    # __range from Django ORM don't resolve task, because of doesn't include dates
    # note that there are posts without date "created_at" in DB. But that one means that post was deleted

    start_date = time_zone.localize(
        datetime(start_year, start_month, start_day))
    finish_date = time_zone.localize(
        datetime(finish_year, finish_month, finish_day))

    finish_date += timedelta(days=1)

    affilated_logs = AffilateLogs.objects.filter(
        created_at__gte=start_date).filter(created_at__lte=finish_date).all()

    affilate_relations = AffilateRelation.objects.filter(
        created_at__gte=start_date).filter(created_at__lte=finish_date).exclude(
        creator_id__isnull=True).values_list('creator_id').distinct()

    logs_distinct_users = AffilateLogs.objects.filter(
        created_at__gte=start_date).filter(created_at__lte=finish_date).values_list('creator_id', flat=True).distinct()

    return affilate_relations, affilated_logs, logs_distinct_users, finish_date, start_date

@auth_required
def affilates_money_stat(request):

    affilate_users_sum = 0
    money = None
    active_users_sum = None
    get_out_monies = None
    users_pay_done = None
    form = DateForm(request.POST)

    if request.method == 'POST':

        affilate_relations, affilated_logs, logs_distinct_users, \
            finish_date, start_date = get_list_of_logs(request.POST)

        affilate_users_sum = len(affilate_relations)
        active_users_sum = 0
        get_out_monies = 0
        users_pay_done = 0

        # how much affilated users are active now

        for row in affilate_relations:

            user = User.objects.get(id=row[0])
            if active_or_not(user) == 'Активен':

                active_users_sum += 1

        # how much monies was given to referal creators (рефевод)

        money = 0

        for row in affilated_logs:

            if row.bonus_amount and row.creator_fee_type and 'MONEY' in row.creator_fee_type:

                money += row.bonus_amount

        # how much monies was get out from club budget for referal payments

        for row in affilated_logs:

            # it's single event in affilate part of project that has creator and doesn't have affilated_user
            if row.bonus_amount and row.affilated_user is None and row.creator_id:

                get_out_monies += row.bonus_amount

        # how much users make payment

        for row in logs_distinct_users:

            if row:

                user = User.objects.get(id=row)
                how_much = len(Payment.objects.filter(created_at__gte=start_date).filter(
                    created_at__lte=finish_date).filter(user=user).filter(status='success').all())
                users_pay_done += how_much

    return render(
        request,
        'pages/stats-affilate-money.html',
        {
            'form': form,
            'money': money,
            'active_users_sum': active_users_sum,
            'affilate_users_sum': affilate_users_sum,
            'get_out_monies': get_out_monies,
            'users_pay_done': users_pay_done
        }
    )

@auth_required
def affilates_days_stat(request):

    form = DateForm(request.POST)
    days_sum = None
    active_users_sum = None
    affilate_users_sum = 0

    if request.method == 'POST':

        affilate_relations, affilated_logs, logs_distinct_users, \
            finish_date, start_date = get_list_of_logs(request.POST)

        affilate_users_sum = len(affilate_relations)
        active_users_sum = 0

        for row in affilate_relations:

            user = User.objects.get(id=row[0])
            if active_or_not(user) == 'Активен':

                active_users_sum += 1

        days_sum = 0

        for row in affilated_logs:

            if row.creator_fee_type and 'DAYS' in row.creator_fee_type:

                days_sum += row.bonus_amount

    return render(
        request,
        'pages/stats-affilate-days.html',
        {
            'form': form,
            'days': days_sum,
            'active_users_sum': active_users_sum,
            'affilate_users_sum': affilate_users_sum
        }
    )

@auth_required
def payment_link(request):
    payments_link = ''
    if request.method == "POST":
        form = PaymentLinkSingleForm(request.POST)
        status = request.POST['status']
        description = request.POST['description']
        email = request.POST['email']
        payments_link = PaymentLink.objects.all()
        if status != '':
            payments_link = payments_link.filter(status=status)
        if description != '':
            payments_link = payments_link.filter(description=description)
        if email != '':
            payments_link = payments_link.filter(email=status)
        payments_link.order_by('-created_at')
    else:
        payments_link = PaymentLink.objects.filter().order_by('-created_at')
        form = PaymentLinkSingleForm

    return render(request, "pages/payment-link.html", {
        "form": form,
        "payments_link": payments_link
    })
