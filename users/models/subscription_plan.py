from uuid import uuid4

from django.db import models

class SubscriptionPlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.TextField(null=False)
    amount = models.IntegerField(default=0)
    description = models.TextField(null=False)
    code = models.TextField(null=False)
    timedelta = models.IntegerField(default=0)
    package_name = models.TextField(null=False)
    package_image = models.TextField(null=False)
    package_price = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "subscription_plan"
