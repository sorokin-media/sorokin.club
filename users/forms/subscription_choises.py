from django.forms import ModelForm
from users.models.subscription import User
from django.forms import CheckboxInput

class ChooseSubscription(ModelForm): 
    class Meta:
        model = User
        fields = ('tg_yesterday_best_posts', 'tg_weekly_best_posts', 'daily_email_digest', 'weekly_email_digest')
        widgets = {'tg_yesterday_best_posts': CheckboxInput(),
        'tg_weekly_best_posts': CheckboxInput(),
        'daily_email_digest': CheckboxInput(),
        'weekly_email_digest': CheckboxInput()}
