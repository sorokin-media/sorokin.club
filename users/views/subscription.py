from users.models.subscription import SubscriptionUserChoise as sub_model
from django.http.response import HttpResponse
from users.forms.subscription_choises import ChooseSubscription as sub_form
from django.shortcuts import render, redirect

from users.models.user import User

def success_subscription(request):
    return render(request, 'users/profile/success_subscription.html')

def subscription_user_choise(request, user):
    if request.method == 'POST':
        sub_model.save_data(request, user)
        form = sub_form(request.POST)
        return redirect('success_subscription')
    user_in_db = User.objects.get(slug=user)
    if sub_model.objects.filter(user_id=user_in_db).exists():
        instance = sub_model.objects.get(user_id=user_in_db)
        form = sub_form(instance=instance)
        return render(request, 'users/profile/subscription_choise.html', {'form': form, 'user': user})
    form = sub_form()
    return render(request, 'users/profile/subscription_choise.html', {'form': form, 'user': user})
