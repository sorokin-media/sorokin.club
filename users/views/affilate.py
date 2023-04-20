# Django imports
from django.shortcuts import redirect, render
from django.http import HttpResponse

# models import
from users.models.affilate_models import AffilateInfo, AffilateLogs
from users.models.user import User

# forms import
from users.forms.affilate_forms import AffilateInfoForm

def pfofile_affilate(request, user_slug):

    user = User.objects.get(slug=user_slug)

    if not AffilateInfo.objects.filter(user_id=user).exists():
        new_one = AffilateInfo()
        new_one.insert_new_one(user)

    if request.method == 'POST':
        return HttpResponse(user_slug)

    form = AffilateInfoForm()
    affilate_info = AffilateInfo.objects.get(user_id=user)
    affilate_logs = AffilateLogs.objects.filter(creator_id=user).all().order_by('time_come_on_intro')

    return render(request, 'users/profile/affilate.html', {
        'form': form,
        'user': user,
        'affilate_info': affilate_info,
        'affilate_logs': affilate_logs
    })
