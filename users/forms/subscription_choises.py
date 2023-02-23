from django.forms import Form
from users.models.subscription import User
from django.forms import CheckboxInput, BooleanField

class ChooseSubscription(Form):

    YES_NO = (
        (True, 'Yes'),
        (False, 'No')
    )

    daily_email_digest = BooleanField(label='Ежедневная e-mail рассылка', required=False, widget=CheckboxInput())
    weekly_email_digest = BooleanField(label='Еженедельная e-mail рассылка', required=False, widget=CheckboxInput())
    tg_yesterday_best_posts = BooleanField(label='Лучшие посты и самые интересные интро за вчерашний день', required=False, widget=CheckboxInput())
    tg_weekly_best_posts = BooleanField(label="Лучшие посты и интересные интро за прошедшую неделю", required=False, widget=CheckboxInput())