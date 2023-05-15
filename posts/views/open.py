from django.conf import settings
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render, HttpResponse

from auth.helpers import check_user_permissions, auth_required
from club.exceptions import AccessDenied, ContentDuplicated, RateLimitException
from common.request import ajax_request
from posts.forms.compose import POST_TYPE_MAP, PostTextForm
from posts.models.linked import LinkedPost
from posts.models.post import Post
from posts.models.subscriptions import PostSubscription
from posts.models.views import PostView
from posts.models.votes import PostVote
from posts.renderers import render_post
from search.models import SearchIndex

from common.pagination import paginate

def open_posts(request):
    posts = Post.objects.filter(is_public=True).all()
    return render(
        request,
        'open.html',
        {
            "posts": paginate(request, posts)
        }
    )
