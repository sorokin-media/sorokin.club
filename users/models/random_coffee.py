from django.db import models
from uuid import uuid4

from datetime import datetime
from datetime import timedelta

from users.models.user import User

import pytz

class RandomCoffee(models.Model):

    class Meta:
        db_table = 'random_coffee'

    TRUE_FALSE_CHOICES = (
        (True, 'Да'),
        (False, 'Нет')
    )
    user = models.ForeignKey(User, related_name="random_coffee", on_delete=models.CASCADE, db_column='user')
    random_coffee_is = models.BooleanField(default=False,
                                           verbose_name='Я хочу участвовать в клубном Random Coffee!')
    random_coffee_tg_link = models.CharField(null=True,
                                             max_length=128,
                                             verbose_name='Ваш Телеграм для связи с собеседником')
    random_coffee_today = models.BooleanField(default=True)
    random_coffee_past_partners = models.TextField(null=True)
    random_coffee_last_partner_id = models.UUIDField(null=True)
    coffee_activation_time = models.DateTimeField(verbose_name='Время активации опции',
                                                  null=True)
    coffee_done = models.IntegerField(default=0)
    coffee_deny = models.IntegerField(default=0)



    def set_activation_coffee_time(self):
        time_zone = pytz.UTC
        now = datetime.now(time_zone)
        self.coffee_activation_time = now
        self.save()


class RandomCoffeeLogs(models.Model):

    class Meta:
        db_table = 'random_coffee_logs'

    user = models.ForeignKey(User, related_name="random_coffee_logs_user",
                             on_delete=models.CASCADE,
                             db_column='user')
    user_buddy = models.ForeignKey(User, related_name="random_coffee_logs_user_buddy",
                                   on_delete=models.CASCADE,
                                   db_column='user_buddy')
    feedback = models.JSONField(null=True)
    date = models.DateField(null=True)

    def set_today_date(self):
        today = datetime.utcnow().date()
        self.date = today
        self.save()
