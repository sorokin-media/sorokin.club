# Python imports
from datetime import datetime
from uuid import uuid4
from uuid import UUID
import pytz

# Django ORM import
from django.db.models import Max
from django.db.models import Q

# Django imports
from django.conf import settings
from django.db import models

# import models
from users.models.user import User
from users.models.subscription_plan import SubscriptionPlan

# COMMENT FOR FUTURE UPDATES
#
# don't forget that there are \landing\views.py
# and open_posts.py
# where updates must be too. of just search by <if 'affilate_p'>

# CHANGE classmethods for creating new one

class AffilateInfo(models.Model):
    ''' This stores data about a user who has connected to the referral program and their referral program settings '''

    AFFILATE_CHOICES = [
        ('DAYS', 'Дни'),
        ('MONEY', 'Деньги')

    ]

    class Meta:
        db_table = 'affilate_info'

    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    parametr = models.UUIDField(unique=True, default=uuid4, editable=False, max_length=16)
    percent = models.PositiveSmallIntegerField(default=10, editable=True)
    fee_type = models.CharField(default='Дни', verbose_name='Как я хочу получать вознаграждение',
                                choices=AFFILATE_CHOICES, max_length=24)
    sum = models.DecimalField(default=0, decimal_places=1, max_digits=10)

    def insert_new_one(self, user):

        self.user_id = user
        self.save()


class AffilateVisit(models.Model):
    ''' This stores data about users who arrived at the website via a referral link '''

    class Meta:
        db_table = 'affilate_visit'

    creator_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True,
                                   related_name='visit_affilate_creator', db_column='creator_id')
    id = models.UUIDField(primary_key=True, default=uuid4)
    ref_url = models.CharField(max_length=248, null=True, editable=True)
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.UUIDField(default=uuid4, null=True)

    def generate_uniqie_uuid_value(self):

        new_uuid = uuid4()

        while AffilateVisit.objects.filter(code=new_uuid).exists():

            new_uuid = uuid4()

        return new_uuid

    def insert_first_time(self, p_value, code, url):

        # if it's correct value of p, there is a user who is ref creator with this link
        if p_value and AffilateInfo.objects.filter(parametr=UUID(p_value)).exists():
            self.creator_id = AffilateInfo.objects.get(parametr=UUID(p_value)).user_id
        elif code and AffilateVisit.objects.filter(code=code).exists():
            self.creator_id = AffilateVisit.objects.filter(code=code).first().creator_id
        if self.creator_id is None:
            return False
            # if it's first come to site of new_ser
        if not code:
            self.code = self.generate_uniqie_uuid_value()
            self.ref_url = url
            self.save()
            return True
        # if it is not first coming to site of user
        else:
            self.code = code
            self.ref_url = url
            self.save()
            return True


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

    created_at = models.DateTimeField(auto_now_add=True)
    creator_id = models.ForeignKey(User, related_name='creator_of_affilate',
                                   on_delete=models.CASCADE, db_column='creator_id')
    affilated_user = models.ForeignKey(User, related_name='affilated_user',
                                       on_delete=models.CASCADE, db_column='affilated_user', null=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    last_product = models.ForeignKey(SubscriptionPlan, related_name='product_for_affilate', on_delete=models.CASCADE, null=True)
