from django.shortcuts import render

from posts.models.post import Post

from users.models.affilate_models import AffilateVisit

from common.pagination import paginate

from datetime import datetime, timedelta
from django.db.models import Q

def open_posts(request):

    if not request.me:

        identify_string = None

        if 'p' in request.GET.keys():
            # getlist instead of keys() because of exception of dublicated ?p= in URL

            p_value = request.GET.getlist('p')[0]
            identify_string = None

        else:

            p_value = None

        if 'affilate_p' in request.COOKIES.keys() and not p_value:

            identify_string = request.COOKIES.get('affilate_p')

        new_one = AffilateVisit()
        done = new_one.insert_first_time(
            p_value=p_value,
            code=identify_string,
            url=request.build_absolute_uri()
        )
        if done:
            cookie = new_one.code
        else:
            cookie = None
    else:
        cookie = None

    posts = Post.objects.filter(is_public=True).exclude(is_visible=False).all()

    if cookie:

        return_ = render(
            request,
            "open.html",
            {
                "posts": paginate(request, posts)
            }
        )
        expires = datetime.now() + timedelta(days=3650)
        return_.set_cookie('affilate_p', cookie, expires=expires)
        return return_

    return render(
        request,
        "open.html",
        {
            "posts": paginate(request, posts)
        }
    )
