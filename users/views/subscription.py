from users.models.subscription import SubscriptionUserChoise as sub_model
from django.http.response import HttpResponse
from users.forms.subscription_choises import ChooseSubscription as sub_form
from django.shortcuts import render, redirect

from users.models.user import User
from users.models.random_coffee import RandomCoffee
from users.forms.subscription_choises import RandomCoffee as coffee_form

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

def random_coffee(request, user):
    if request.method == 'POST':
        user = User.objects.get(slug=user)
        coffee = RandomCoffee()
        coffee.user = user
        coffee.random_coffee_is = request.POST.get('random_coffee_is')
        coffee.random_coffee_tg_link = request.POST.get('random_coffee_tg_link')
        coffee.save()
        return render(request, 'users/profile/random_coffee_success.html')
    form = coffee_form()
    return render(request, 'users/profile/random_coffee.html', {'form': form, 'user': user})
