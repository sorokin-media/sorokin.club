from django.forms import ModelForm
from users.models.subscription import SubscriptionUserChoise
from users.models.random_coffee import RandomCoffee

class ChooseSubscription(ModelForm):
    class Meta:
        model = SubscriptionUserChoise
        fields = ('tg_yesterday_best_posts', 'tg_weekly_best_posts', 'daily_email_digest', 'weekly_email_digest')

class RandomCoffee(ModelForm):
    class Meta:
        model = RandomCoffee
        fields = ('random_coffee_is', 'random_coffee_tg_link')
