from django.conf import settings

from club import features
from common.data.expertise import EXPERTISE

# import models
from posts.models.post import Post

def settings_processor(request):
    return {
        "settings": settings
    }


def data_processor(request):
    return {
        "global_data": {
            "expertise": EXPERTISE,
        }
    }


def features_processor(request):
    return {"features": features}

def telegram_add_processor(request):
    ignore_paths = [
        '/intro/',
        '/join/',
        '/club/',

        '/auth/login/',
        '/auth/logout/',
        '/auth/patreon/',
        '/auth/patreon_callback/',
        '/auth/email/',
        '/auth/email/code/',
        '/auth/external/',

        '/monies/',
        '/monies/crypto/',
        '/monies/done/',
        '/monies/membership_expired/',
        '/monies/stripe/webhook/',
        '/monies/coinbase/webhook/',
        '/monies/unitpay/pay/',
        '/monies/unitpay/webhook/',
    ]
    return {"telegram_modal_ignore_paths": ignore_paths}

def robots_noindex(request):
    ''' add metatag for search engine to html  '''
    noindex_urls = [
        '/network',
        '/people',
        '/monies',
        '/announce',
        '/admin',
        '/?type=search',
        '/edit',
        '/stats-buddy',
        '/room',
        '/auth',
        'cool_intro',
        'day_helpfullness',
        'telegram_message',
        '/info_tg_format',
        'stat'

    ]
    if any(url in request.path for url in noindex_urls):
        return {"noindex": True}
    try:
        post_id = request.session.pop('post_id', None)
        post = Post.objects.get(id=post_id)
        if not post.is_public:
            return {"noindex": True}
    except:
        pass
    return {}