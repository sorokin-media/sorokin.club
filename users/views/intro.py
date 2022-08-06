import json
from django.shortcuts import redirect, render
from django_q.tasks import async_task

from auth.helpers import auth_required
from notifications.telegram.users import notify_profile_needs_review
from posts.models.post import Post
from users.forms.intro import UserIntroForm
from users.models.geo import Geo
from users.models.user import User
from pprint import pprint


@auth_required
def intro(request):
    pprint(request)
    if request.me.moderation_status == User.MODERATION_STATUS_APPROVED:
        return redirect("profile", request.me.slug)
    if request.method == "PUT":
        user = request.me
        data = json.loads(request.body)
        user.bio = data["bio"]
        user.city = data["city"]
        user.company = data["company"]
        user.country = data["country"]
        user.position = data["position"]
        user.save()
        existing_intro = Post.get_user_intro(request.me)
        if not existing_intro:
            existing_intro = Post.upsert_user_intro(
                user, data["intro"], is_visible=False
            )
        else:
            existing_intro.text = data["intro"]
            existing_intro.html = data["intro"]
            existing_intro.save()
    if request.method == "POST":
        form = UserIntroForm(request.POST, request.FILES, instance=request.me)
        if form.is_valid():
            user = form.save(commit=False)

            # send to moderation
            user.moderation_status = User.MODERATION_STATUS_ON_REVIEW
            user.save()

            # create intro post
            intro_post = Post.upsert_user_intro(
                user, form.cleaned_data["intro"], is_visible=False
            )

            Geo.update_for_user(user)

            # notify moderators to review profile
            async_task(notify_profile_needs_review, user, intro_post)

            return redirect("on_review")
    else:
        existing_intro = Post.get_user_intro(request.me)
        form = UserIntroForm(
            instance=request.me,
            initial={"intro": existing_intro.text if existing_intro else ""},
        )

    return render(request, "users/intro.html", {"form": form})
