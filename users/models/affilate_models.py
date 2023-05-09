from datetime import datetime, timedelta
from uuid import uuid4
from uuid import UUID
import pytz
import decimal

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


'''
Модель AffilateInfo => участники реферальной программы, создатели ссылок
Модель AffilateVisit => фиксирует визиты пришедших по реферальной программе
Модель AffilateLogs => фиксирует списывания, ничего больше

'''

class AffilateInfo(models.Model):
    ''' This stores data about a user who has connected to the referral program and their referral program settings '''
    DEFAULT_LINK = 'http://127.0.0.1:8000/post/2/'

    AFFILATE_CHOICES = [
        ('DAYS', 'Дни'),
        ('MONEY', 'Деньги')

    ]

    class Meta:
        db_table = 'affilate_info'

    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    parametr = models.UUIDField(unique=True, default=uuid4, editable=False, max_length=16)
    url = models.CharField(default=DEFAULT_LINK, max_length=248)
    percent = models.PositiveSmallIntegerField(default=10, editable=True)
    fee_type = models.CharField(default='Дни', verbose_name='Как я хочу получать вознаграждение',
                                choices=AFFILATE_CHOICES, max_length=24)
    sum = models.DecimalField(default=0, decimal_places=1, max_digits=10)

    def insert_new_one(self, user, link=DEFAULT_LINK):

        self.user_id = user
        self.url = self.DEFAULT_LINK + '?p=' + str(self.parametr)
        self.save()


class AffilateVisit(models.Model):
    ''' This stores data about users who arrived at the website via a referral link '''

    DEFAULT_LINK = 'http://127.0.0.1:8000/post/2/'

    class Meta:
        db_table = 'affilate_visit'

    creator_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True,
                                   related_name='visit_affilate_creator', db_column='creator_id')
    id = models.UUIDField(primary_key=True, default=uuid4)
    ref_url = models.CharField(max_length=248, null=True, editable=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # if last_page_view_time is Null, than user mane only one page view
    last_page_view_time = models.DateTimeField(null=True)
    code = models.UUIDField(unique=True, default=uuid4, null=True)
    affilate_status = models.CharField(max_length=48, default='user visited site')

    def insert_first_time(self, p_value, code):

        # case #0: == 1 new_user, == 1 author_of_ref
        # case #1: > 1 authors of ref, but == 1 new_user
        # a) come by first ref and no registrated -> there is no in table
        # b) come by second ref and not registrated -> there is in table AND
        # case #2: == 1 author of ref, but > 1 new_user
        # case #3: new_user open second time same link

        if AffilateInfo.objects.filter(parametr=UUID(p_value)).exists():
            self.creator_id = AffilateInfo.objects.get(parametr=UUID(p_value)).user_id
        else:
            return False
        # if it's first come to site of new_ser
        if not code:
            self.save()
            return True

        # if it is not first coming to site of user
        else:
            previous_refs = AffilateVisit.objects.filter(
                code=code).values_list('creator_id', flat=True)

            dublicated_creator = AffilateInfo.objects.filter(user_id__in=previous_refs).first()
            if dublicated_creator:
                # If this is not a page view that has already occurred before
                if not AffilateVisit.objects.filter(
                        creator_id=self.creator_id).filter(
                        code=code).filter(
                        affilate_status='user visited site').exists():
                    self.save()
                    return True
                else:
                    # user not visited for the first time, make more than on page view
                    db_row = AffilateVisit.objects.filter(creator_id=self.creator_id).filter(
                        code=code).filter(affilate_status='user visited site').first()
                    time_zone = pytz.UTC
                    db_row.last_page_view_time = time_zone.localize(datetime.utcnow())
                    db_row.save()
            else:
                self.code = code
                self.save()
                return True
        return False


class AffilateLogs(models.Model):
    ''' This stores data about users who arrived at the website via a referral link '''
    # variants of affilate_status:
    #
    # 1. user visited site -> come but not registrate
    # 2. come to intro form -> come and go throw payment stage, come to intro
    # 3. manual by admin-interface -> admin add by interface affilating
    # 4. get money -> admin get money from account of user by interface

    class Meta:
        db_table = 'affilate_logs'

    creator_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True,
                                   related_name='logs_affilate_creator', db_column='creator_id')
    affilated_user = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                       related_name='logs_affilated_user', db_column='affilated_user')
    creator_fee_type = models.CharField(choices=AffilateInfo.AFFILATE_CHOICES, null=True, max_length=24)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    code = models.UUIDField(unique=True, default=uuid4, null=True)
    comment = models.CharField(null=True, max_length=512)
    percent_log = models.PositiveSmallIntegerField(default=10, editable=True, null=True)
    bonus_amount = models.PositiveIntegerField(null=True)

    def manual_insert(self, creator_slug, affilated_user, percent):

        time_zone = pytz.UTC
        now = time_zone.localize(datetime.utcnow())

        creator = User.objects.get(slug=creator_slug)

        self.creator_id = creator
        self.percent_log = percent
        self.code = None
        self.affilated_user = affilated_user
        self.comment = f'admin set {creator.slug} as fereral creator for {affilated_user.slug}'
        creator.save()
        self.save()

    def admin_get_money(self, user, admin_comment, money):

        self.creator_id = user
        self.comment = admin_comment
        self.percent_log = None
        self.affilated_user = None
        self.bonus_amount = money
        self.code = None
        self.save()

# to save relation of new user and user, that used referal programm
class AffilateRelation(models.Model):
    ''' This stores data about the relationship between the referrer and the referred user '''
    class Meta:
        db_table = 'affilate_relation'

    code = models.ForeignKey(AffilateVisit, to_field='code', on_delete=models.CASCADE,
                             db_column='unique_code', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    creator_id = models.ForeignKey(User, related_name='creator_of_affilate',
                                   on_delete=models.CASCADE, db_column='creator_id')
    affilated_user = models.ForeignKey(User, related_name='affilated_user',
                                       on_delete=models.CASCADE, db_column='affilated_user', null=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    percent = models.PositiveSmallIntegerField(default=10, editable=True)
    fee_type = models.CharField(default='Дни', choices=AffilateInfo.AFFILATE_CHOICES, max_length=24)