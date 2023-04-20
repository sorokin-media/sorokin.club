from datetime import datetime, timedelta
from uuid import uuid4
from uuid import UUID
import pytz

# Django ORM import
from django.db.models import Max
from django.db.models import Q

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import F

from users.models.user import User
from common.models import ModelDiffMixin
from utils.slug import generate_unique_slug
from utils.strings import random_string


class AffilateInfo(models.Model):

    DEFAULT_LINK = 'http://127.0.0.1:8000/post/2/'

    AFFILATE_CHOICES = [
        ('MONEY', 'Деньги'),
        ('DAYS', 'Дни')
    ]

    class Meta:
        db_table = 'affilate_info'

    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    parametr = models.UUIDField(unique=True, default=uuid4, editable=False, max_length=16)
    url = models.CharField(default=DEFAULT_LINK, max_length=248)
    percent = models.PositiveSmallIntegerField(default=10)
    fee_type = models.CharField(default='Дни', verbose_name='Как я хочу получать вознаграждение',
                                choices=AFFILATE_CHOICES, max_length=24)
    sum = models.DecimalField(null=True, decimal_places=1, max_digits=10)

    def insert_new_one(self, user, link=DEFAULT_LINK):

        self.user_id = user
        self.url = self.DEFAULT_LINK + '?' + str(self.parametr)
        self.save()


class AffilateVisit(models.Model):

    class Meta:
        db_table = 'affilate_visit'

    id = models.UUIDField(primary_key=True, default=uuid4)
    ref = models.CharField(max_length=248, null=True, editable=True)
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.UUIDField(unique=True, default=uuid4, max_length=8)


class UserAffilate(models.Model):

    class Meta:
        db_table = 'user_affilate'

    affilate_id = models.ForeignKey(AffilateInfo, on_delete=models.CASCADE, db_column='affilate_id', null=True)
    unique_code = models.ForeignKey(AffilateVisit, to_field='code', on_delete=models.CASCADE, db_column='unique_code')
    created_at = models.DateTimeField(auto_now_add=True)
    creator_id = models.ForeignKey(User, related_name='creator_of_affilate',
                                   on_delete=models.CASCADE, db_column='creator_id')
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)

class AffilateLogs(models.Model):

    ACTION_CHOISES = [
        ('PAY_BY_AFFILATE', 'paid for membership'),
        ('GET_BY_MONEY', 'get money from club')
    ]

# for checking diff between time first come to club and time of registration in club
# also for checking of a mount of comming but not registrated

    AFFILATE_STATUS = [
        ('FIRST_TIME', 'come first time'),
        ('REGISTRATION_DONE', 'come to intro form')
    ]

    class Meta:
        db_table = 'affilate_logs'

    creator_id = models.ForeignKey(User, on_delete=models.CASCADE,
                                   related_name='affilate_creator', db_column='creator_id')
    affilated_user = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                       related_name='affilated_user', db_column='affilated_user')
    affilate_status = models.CharField(choices=AFFILATE_STATUS, max_length=48, default='come first time')
    creator_fee_type = models.CharField(choices=AffilateInfo.AFFILATE_CHOICES, max_length=24)
    type_of_action = models.CharField(null=True, choices=ACTION_CHOISES, max_length=48)
    time_firstly_come = models.DateTimeField(auto_now_add=True)
    time_come_on_intro = models.DateTimeField(null=True)
    identify_new_user = models.UUIDField(unique=True, default=uuid4)
    comment = models.CharField(null=True, max_length=248)

    def insert_first_time(self, p_value, identify_string):

        # case #0: == 1 new_user, == 1 author_of_ref
        # case #1: > 1 authors of ref, but == 1 new_user
        # a) come by first ref and no registrated -> there is no in table
        # b) come by second ref and not registrated -> there is in table AND
        # case #2: == 1 author of ref, but > 1 new_user
        # case #3: new_user open second time same link

        self.creator_id = AffilateInfo.objects.get(parametr=UUID(p_value)).user_id
        self.creator_fee_type = AffilateInfo.objects.get(user_id=self.creator_id).fee_type
        # if it's first come to site of new_ser
        if not identify_string:
            self.save()

        # if it is not first coming to site of user
        else:
            previous_refs = AffilateLogs.objects.filter(
                identify_new_user=identify_string).values_list('creator_id', flat=True)

            dublicated_creator = AffilateInfo.objects.filter(user_id__in=previous_refs).first()
            if dublicated_creator:
                # If this is not a page view that has already occurred before
                if not AffilateLogs.objects.filter(creator_id=self.creator_id).filter(affilate_status='come first time').filter().exists():
                    self.save()

    def insert_on_intro(self, user):

        time_zone = pytz.UTC
        now = time_zone.localize(datetime.utcnow())

        if self.affilate_status != 'come to intro form':

            self.affilated_user = user
            self.time_come_on_intro = now
            self.affilate_status = 'come to intro form'
            self.save()