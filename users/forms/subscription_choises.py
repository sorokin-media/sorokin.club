from django.forms import ModelForm
from users.models.subscription import SubscriptionUserChoise

class ChooseSubscription(ModelForm): 
    class Meta:
        model = SubscriptionUserChoise
        fields = ('tg_yesterday_best_posts', 'tg_weekly_best_posts', 'daily_email_digest', 'weekly_email_digest')
