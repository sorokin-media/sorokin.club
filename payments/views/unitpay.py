import logging
from json import dumps

from django.http import HttpResponse

log = logging.getLogger(__name__)


def unitpay_webhook(request):
    log.info("Unitpay webhook, GET %r, POST %r, META %r", request.GET, request.POST, request.META)

    return HttpResponse(dumps({"result": {"message": "Запрос успешно обработан"}}))
