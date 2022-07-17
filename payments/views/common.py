from datetime import datetime

from django.shortcuts import redirect, render
from users.models.subscription import Subscription
from users.models.subscription_plan import SubscriptionPlan


def membership_expired(request):
    if not request.me:
        return redirect("index")

    if request.me.membership_expires_at >= datetime.utcnow():
        return redirect("profile", request.me.slug)

    plan_subcription = Subscription.objects.filter(default=True).last()
    plans = SubscriptionPlan.objects.filter(subscription_id=plan_subcription.id)

    return render(request, "payments/membership_expired.html", {
        "plans": plans
    })
