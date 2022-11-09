from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import TemplateDoesNotExist

from comments.forms import CommentForm, ReplyForm, BattleCommentForm
from comments.models import Comment
from posts.models.post import Post
from bookmarks.models import PostBookmark
from posts.models.subscriptions import PostSubscription
from posts.models.votes import PostVote
from users.models.mute import Muted
from posts.models.linked import LinkedPost

POSSIBLE_COMMENT_ORDERS = {"created_at", "-created_at", "-upvotes"}


def render_post(request, post, context=None):
    # render "raw" newsletters
    if post.type == Post.TYPE_WEEKLY_DIGEST:
        return HttpResponse(post.html)

    # select votes and comments
    if request.me:
        comments = Comment.objects_for_user(request.me).filter(post=post).all()
        is_bookmark = PostBookmark.objects.filter(post=post, user=request.me).exists()
        is_voted = PostVote.objects.filter(post=post, user=request.me).exists()
        upvoted_at = int(PostVote.objects.filter(post=post, user=request.me).first().created_at.timestamp() * 1000) if is_voted else None
        subscription = PostSubscription.get(request.me, post)
        muted_user_ids = list(Muted.objects.filter(user_from=request.me).values_list("user_to_id", flat=True).all())
        muted_user_ids_our = list(Muted.objects.filter(user_to_id=request.me).values_list("user_from", flat=True).all())
    else:
        comments = Comment.visible_objects(show_deleted=True).filter(post=post).all()
        is_voted = False
        is_bookmark = False
        upvoted_at = None
        subscription = None
        muted_user_ids = []
        muted_user_ids_our = []

    # order comments
    comment_order = request.GET.get("comment_order") or "-upvotes"
    if comment_order in POSSIBLE_COMMENT_ORDERS:
        comments = comments.order_by(comment_order, "created_at")  # additionally sort by time to preserve an order

    # hide deleted comments for battle (visual junk)
    if post.type == Post.TYPE_BATTLE:
        comments = comments.filter(is_deleted=False)

    flag_muted = False
    if post.author_id in muted_user_ids:
        flag_muted = True
    if post.author_id in muted_user_ids_our:
        flag_muted = True

    comment_form = CommentForm(initial={'text': post.comment_template}) if post.comment_template else CommentForm()
    context = {
        **(context or {}),
        "post": post,
        "comments": comments,
        "comment_form": comment_form,
        "comment_order": comment_order,
        "reply_form": ReplyForm(),
        "is_bookmark": is_bookmark,
        "is_voted": is_voted,
        "upvoted_at": upvoted_at,
        "subscription": subscription,
        "muted_user_ids": muted_user_ids,
        "flag_muted": flag_muted,
    }

    # TODO: make a proper type->form mapping here in future
    if post.type == Post.TYPE_BATTLE:
        context["comment_form"] = BattleCommentForm()

    action = request.POST.get("action")
    if action == "publish":
        post.publish()
        LinkedPost.create_links_from_text(post, post.text)
        return redirect("show_post", post.type, post.slug)
    if post.type == 'idea':
        return render(request, "posts/show/idea.html", context)
    if post.type == 'event':
        return render(request, "posts/show/event.html", context)
    if post.type == 'question':
        return render(request, "posts/show/question.html", context)
    if post.type == 'link':
        return render(request, "posts/show/link.html", context)
    if post.type == 'battle':
        return render(request, "posts/show/battle.html", context)
    if post.type == 'post':
        return render(request, "posts/show/post.html", context)
    try:
        return render(request, f"posts/show/{post.type}.html", context)
    except TemplateDoesNotExist:
        return render(request, "posts/show/post.html", context)
