from django.shortcuts import render

from posts.models.post import Post

from users.models.affilate_models import AffilateVisit

from common.pagination import paginate

from datetime import datetime, timedelta

def open_posts(request):

    if not request.me:

        if 'p' in request.GET.keys():
            # getlist instead of keys() because of exception of dublicated ?p= in URL

            p_value = request.GET.getlist('p')[0]

            new_one = AffilateVisit()
            identify_string = None

            if 'affilate_p' in request.COOKIES.keys():

                identify_string = request.COOKIES.get('affilate_p')

            done = new_one.insert_first_time(p_value, identify_string)
            if done:
                cookie = new_one.code
            else:
                cookie = None
    else:
        cookie = None

    posts = Post.objects.filter(is_public=True).all()

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
