from users.models.user import User
from payments.models import Payment

from django.http.response import HttpResponse

def dmitry_tests(request):

    u = User.objects.get(slug='fromseconddev')
    pay = Payment()
    pay.user = u
    pay.amount = 1000
    pay.save()

#    u = User.objects.get(slug='moneytest2')
#    pay = Payment()
#    pay.user = u
#    pay.amount = 1000
#    pay.save()

    return HttpResponse('done')
