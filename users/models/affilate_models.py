from datetime import datetime, timedelta
from uuid import uuid4
import pytz

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import F

from users.models.user import User
from common.models import ModelDiffMixin
from utils.slug import generate_unique_slug
from utils.strings import random_string

class AffiliateInfo(models.Model):

    AFFILATE_CHOICES = [
        {'MONEY':'Деньги'},
        {'DAYS': 'Дни'}
    ]

    class Meta:
        db_table = 'affiliate_info'
    
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    link = models.UUIDField(unique=True, default=uuid4, editable=False, max_length=16)
    percent = models.PositiveSmallIntegerField(default=10)
    fee_type = models.CharField(default=AFFILATE_CHOICES['DAYS'], choices=AFFILATE_CHOICES)
    sum = models.DecimalField(null=True)

class AffilateVisit(models.Model):

    class Meta:
        db_table = 'affiliate_visit'

    id = models.UUIDField(primary_key=True, default=uuid4)
    ref = models.CharField(max_length=248, null=True, editable=True)
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.UUIDField(unique=True, default=uuid4, max_length=8)

class UserAffilate(models.Model):

    class Meta:
        dt_table = 'user_affiliate'

    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    affiliate_id = models.ForeignKey(AffiliateInfo, on_delete=models.CASCADE)
    unique_code = models.ForeignKey(AffilateVisit, to_field='code', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    creator_id = models.ForeignKey(User, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)

