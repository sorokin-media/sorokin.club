# Python imports
import datetime as DT
import pprint
import time
from datetime import datetime, timedelta
import pytz
import json

# Django imports
from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404, render
from django.http import Http404
from django.shortcuts import render, redirect

# import models
from users.models.user import User
from users.models.random_coffee import RandomCoffee, RandomCoffeeLogs
from payments.models import Payment
from posts.models.post import Post
from comments.models import Comment
from users.models.subscription import Subscription
from users.models.subscription_plan import SubscriptionPlan
from users.models.affilate_models import AffilateLogs

# import forms
from stats.forms.money import DateForm

# custom classes imports
from auth.helpers import auth_required
from users.templatetags.users import active_or_not

# import confid data
from club.settings import APP_HOST as host

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

@auth_required
def affilates_money_stat(request):

    affilate_users_sum = 0
    money = None
    active_users_sum = None
    form = DateForm(request.POST)
    
    if request.method == 'POST':

        time_zone = pytz.UTC
        range_date = request.POST['date-range']
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

        finish_date += timedelta(days=1z)

        affilated_logs = AffilateLogs.objects.filter(
            affilate_time_was_set__gte=start_date).filter(affilate_time_was_set__lte=finish_date).all()

        print(affilated_logs)

        money = 0
        active_users_sum = 0
        
        for row in affilated_logs:

            if 'Bonus Money:' in row.comment:

                affilate_users_sum += 1
                money += float(row.comment.replace('Bonus Money: ', ''))
                user = row.affilated_user

                if active_or_not(user) == 'Активен':
                
                    active_users_sum += 1

    return render(
        request,
        'pages/stats-affilate-money.html',
        {
            'form': form,
            'money': money,
            'active_users_sum': active_users_sum,
            'affilate_users_sum': affilate_users_sum
        }
    )

@auth_required
def affilates_days_stat(request):

    form = DateForm(request.POST)
    days_sum = None
    active_users_sum = None
    affilate_users_sum = 0
    
    if request.method == 'POST':

        time_zone = pytz.UTC
        range_date = request.POST['date-range']
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

        affilated_logs = AffilateLogs.objects.filter(
            affilate_time_was_set__gte=start_date).filter(affilate_time_was_set__lte=finish_date).all()

        days_sum = 0
        active_users_sum = 0

        for row in affilated_logs:

            if 'Bonus Days' in row.comment:

                affilate_users_sum += 1
                days_sum += int(row.comment.replace('Bonus Days: ', ''))
                user = row.affilated_user

                if active_or_not(user) == 'Активен':

                    active_users_sum += 1

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
