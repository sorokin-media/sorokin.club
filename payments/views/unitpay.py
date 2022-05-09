import hashlib
import logging
from json import dumps

from django.conf import settings
from django.http import HttpResponse

log = logging.getLogger(__name__)


def unitpay_webhook(request):
    log.info("Unitpay webhook, GET %r", request.GET)

    method = None
    signature = None
    params = dict()

    for k, v in request.GET:
        if k == "method":
            method = v

        elif k == "params[signature]":
            signature = v

        else:
            k = k.replace("params[", "").replace("]", "")
            params[k] = v

    string = "{up}".join([method] + [params[k] for k in sorted(params.keys())] + [settings.UNITPAY_SECRET_KEY])
    counted_signature = hashlib.sha256(string.encode()).hexdigest()

    if signature == counted_signature:
        return HttpResponse(dumps({"result": {"message": "Запрос успешно обработан"}}))

    else:
        return HttpResponse(dumps({"error": {"message": "Ошибка в подписи"}}), status_code=400)
