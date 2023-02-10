from uuid import uuid4

from django.db import models
from users.models.user import User

class Subscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.TextField(null=False)
    default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "subscription"

# field is name of subscription's type
# tg - telegram
# em - email
class SubscriptionUserChoise(models.Model):

    TRUE_FALSE_CHOICES = (
        (True, 'Yes'),
        (False, 'No')
    )

    tg_yesterday_best_posts = models.BooleanField(default=False,
                                                  verbose_name='Лучшие посты и самые интересные интро за вчерашний день',
                                                  choices=TRUE_FALSE_CHOICES)
    tg_weekly_best_posts = models.BooleanField(default=False,
                                               verbose_name="Лучшие посты и интересные интро за прошедшую неделю",
                                               choices=TRUE_FALSE_CHOICES)
    user_id = models.ForeignKey(User, related_name='subscription_user_choises',
                                on_delete=models.CASCADE, db_column='user_id')

    class Meta:
        db_table = 'subscription_user_choises'

    def save_data(request, user):
        user = User.objects.filter(slug=user).first()
        if SubscriptionUserChoise.objects.filter(user_id=user).exists():
            sub_list = SubscriptionUserChoise.objects.get(user_id=user)
            sub_list.tg_yesterday_best_posts = request.POST.get('tg_yesterday_best_posts')
            sub_list.tg_weekly_best_posts = request.POST.get('tg_weekly_best_posts')
            sub_list.save()
        else:
            sub_list = SubscriptionUserChoise()
            sub_list.user_id = user
            sub_list.tg_yesterday_best_posts = request.POST.get('tg_yesterday_best_posts')
            sub_list.tg_weekly_best_posts = request.POST.get('tg_weekly_best_posts')
            
            sub_list.save()
