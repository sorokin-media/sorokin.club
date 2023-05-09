# Django imports
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.db.models import Q
from django.contrib import messages

# models import
from users.models.affilate_models import AffilateInfo, AffilateLogs, AffilateRelation
from users.models.user import User

# forms import
from users.forms.affilate_forms import AffilateInfoForm

def pfofile_affilate(request, user_slug):

    user = User.objects.get(slug=user_slug)

    if not AffilateInfo.objects.filter(user_id=user).exists():
        new_one = AffilateInfo()
        new_one.insert_new_one(user)

    if request.method == 'POST':
        affilate_info_row = AffilateInfo.objects.get(user_id=user)
        form = AffilateInfoForm(request.POST, instance=affilate_info_row)
        if form.is_valid():
            form.save()
            return redirect('profile', user_slug=user_slug)

    form = AffilateInfoForm(
        instance=AffilateInfo.objects.get(
            user_id=user
        )
    )
    affilate_info = AffilateInfo.objects.get(user_id=user)
    affilate_logs = AffilateLogs.objects.filter(creator_id=user).exclude(affilated_user__isnull=True).all().order_by('created_at')
    get_money_logs = AffilateLogs.objects.filter(creator_id=user).filter(affilated_user__isnull=True).all()

    return render(request, 'users/profile/affilate.html', {
        'form': form,
        'user': user,
        'affilate_info': affilate_info,
        'affilate_logs': affilate_logs,
        'get_money_logs': get_money_logs
    })

def affilate_list(request, user_slug):

    u = User.objects.get(slug=user_slug)

#    slug_list = AffilateLogs.objects.filter(creator_id=u).filter(Q(affilate_status='come to intro form') | Q(
#        affilate_status='manual by admin-interface')).values_list("affilated_user", flat=True)
    slug_list = AffilateRelation.objects.filter(creator_id=u).values_list("affilated_user", flat=True)

    affilate_list = [User.objects.get(id=user_id) for user_id in slug_list]

    return render(
        request,
        'users/profile/affilate_list.html',
        {
            'affilate_list': affilate_list,
            'user': u
        }
    )
    

def get_affilate_money(request, user_slug):

    u = User.objects.get(slug=user_slug)
    aff_info_obj = AffilateInfo.objects.get(user_id=u)

    if request.method == 'POST':

        try:

            money_sum = float(request.POST['sumField'])
            comment = str(request.POST['commentField'])

            aff_info_obj.sum = float(aff_info_obj.sum) - money_sum
            aff_info_obj.save()
            new_one = AffilateLogs()
            new_one.admin_get_money(
                user=u,
                admin_comment=comment,
                money=money_sum
            )
            request.POST = None
            return redirect('profile', user_slug=user_slug)
        except Exception:
            messages.error(request, 'Что-то пошло не так. Сообщите Дмитрию, пожалуйста.')
            return render(
                request,
                'users/profile/get_affilate_money.html',
                {
                    'user': u,
                    'aff_money': aff_info_obj.sum
                },
                messages
            )

    return render(
        request,
        'users/profile/get_affilate_money.html',
        {
            'user': u,
            'aff_money': aff_info_obj.sum
        }
    )
