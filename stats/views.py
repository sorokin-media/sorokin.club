from django.shortcuts import render
import datetime as DT
import pprint
from django.shortcuts import render, redirect

from auth.helpers import auth_required
from users.models.user import User
from payments.models import Payment
from posts.models.post import Post
from stats.forms.money import DateForm
from comments.models import Comment


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
                if payment_one and int(dt.timestamp()) > + int(datetime_for) and int(dt.timestamp()) <= int(
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
