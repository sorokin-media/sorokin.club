from django.forms import Form, ModelForm
from users.models.subscription import User
from django.forms import CheckboxInput, BooleanField
from users.models.random_coffee import RandomCoffee

class ChooseSubscription(ModelForm):
    class Meta:
        model = User
        fields = {
            "daily_email_digest",
            "weekly_email_digest",
            "tg_yesterday_best_posts",
            "tg_weekly_best_posts",
            "day_helpfullness_digest"
        }

    YES_NO = (
        (True, 'Yes'),
        (False, 'No')
    )

    daily_email_digest = BooleanField(label='Ежедневная e-mail рассылка',
                                            required=False,
                                            widget=CheckboxInput())
    weekly_email_digest = BooleanField(label='Еженедельная e-mail рассылка',
                                             required=False,
                                             widget=CheckboxInput())
    tg_yesterday_best_posts = BooleanField(label='Лучшие посты и самые интересные интро за вчерашний день в Telegram',
                                                 required=False,
                                                 widget=CheckboxInput())
    tg_weekly_best_posts = BooleanField(label="Лучшие посты и интересные интро за прошедшую неделю в Telegram",
                                              required=False,
                                              widget=CheckboxInput())
    day_helpfullness_digest = BooleanField(label="Полезности сегодняшего дня в Telegram",
                                           required=False,
                                           widget=CheckboxInput())
    

class RandomCoffee(ModelForm):
    class Meta:
        model = RandomCoffee
        fields = ('random_coffee_is', 'random_coffee_tg_link')
