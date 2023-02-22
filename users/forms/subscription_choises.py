from django.forms import ModelForm
from users.models.subscription import User

class ChooseSubscription(ModelForm): 
    class Meta:
        model = User
        fields = ('tg_yesterday_best_posts', 'tg_weekly_best_posts', 'daily_email_digest', 'weekly_email_digest')
