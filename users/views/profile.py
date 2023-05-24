from django.conf import settings
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect, get_object_or_404, render

from auth.helpers import auth_required
from badges.models import UserBadge
from comments.models import Comment
from common.pagination import paginate
from common.request import ajax_request
from posts.models.post import Post
from search.models import SearchIndex
from users.forms.profile import ExpertiseForm
from users.models.achievements import UserAchievement
from users.models.expertise import UserExpertise
from users.models.friends import Friend
from users.models.mute import Muted
from users.models.tags import Tag, UserTag
from users.models.user import User
from users.forms.profile import CoffeeForm
from users.models.random_coffee import RandomCoffee
from users.utils import calculate_similarity
from bs4 import BeautifulSoup
import base64

from bot.sending_message import MessageToDmitry

# for affilating admin imports
from django.contrib import messages
from users.models.affilate_models import AffilateLogs, AffilateInfo, AffilateRelation

# import custom class for sending messages
from bot.sending_message import TelegramCustomMessage

text_for_new_user = "<strong>Привет! Рандом Кофе подключен!</strong>\n\n"\
    "Каждый понедельник я буду рекомендовать тебе новых классных собеседников. \n\n"\
    "Если ты не захочешь ни с кем знакомиться на какой-то из недель - у тебя будет "\
    "возможность отказаться перед распределением собеседников, я пришлю специальное "\
    "сообшение.\n\n"\
    "Вечером в понедельник я подберу тебе собеседника и вышлю все инструкции.\n\n"\
    "<strong>Добро пожаловать в игру! 🔥</strong>"

@auth_required
def profile(request, user_slug):
    if user_slug == "me":
        return redirect("profile", request.me.slug, permanent=False)

    user = get_object_or_404(User, slug=user_slug)

    if user.moderation_status != User.MODERATION_STATUS_APPROVED and not request.me.is_moderator:
        # hide unverified users
        raise Http404()

    # handle auth redirect
    if user.id == request.me.id:
        goto = request.GET.get("goto")
        if goto and goto.startswith(settings.APP_HOST):
            return redirect(goto)

    # select user tags and calculate similarity with me
    tags = Tag.objects.filter(is_visible=True).all()
    active_tags = {t.tag_id for t in UserTag.objects.filter(user=user).all()}
    similarity = {}
    if user.id != request.me.id:
        my_tags = {t.tag_id for t in UserTag.objects.filter(user=request.me).all()}
        similarity = calculate_similarity(my_tags, active_tags, tags)

    # select other stuff from this user
    intro = Post.get_user_intro(user)
    projects = Post.objects.filter(author=user, type=Post.TYPE_PROJECT, is_visible=True).all()
    badges = UserBadge.user_badges_grouped(user=user)
    achievements = UserAchievement.objects.filter(user=user).select_related("achievement")
    expertises = UserExpertise.objects.filter(user=user).all()
    comments = Comment.visible_objects()\
        .filter(author=user, post__is_visible=True)\
        .order_by("-created_at")\
        .select_related("post")
    posts = Post.objects_for_user(request.me)\
        .filter(is_visible=True)\
        .filter(Q(author=user) | Q(coauthors__contains=[user.slug]))\
        .exclude(type__in=[Post.TYPE_INTRO, Post.TYPE_PROJECT, Post.TYPE_WEEKLY_DIGEST])\
        .order_by("-published_at")
    friend = Friend.objects.filter(user_from=request.me, user_to=user).first()
    muted = Muted.objects.filter(user_from=request.me, user_to=user).first()

    if RandomCoffee.objects.filter(user=user).exists():
        random_coffee_status = RandomCoffee.objects.get(user=user)
        random_coffee_status = random_coffee_status.random_coffee_is
    else:
        random_coffee_status = False

    # code bellow is about affilate programm

    if not AffilateRelation.objects.filter(affilated_user=user).exists():

        if request.method == 'POST':

            affilate_creator_slug = request.POST['SlugField']
            percent = request.POST['PercentSelect']

            try:
                # don't delete. that's for check out exist or not instead of ORM exist method
                form_affilate_creator = User.objects.get(slug=affilate_creator_slug)

                # save logs
                new_one = AffilateLogs()
                new_one.manual_insert(
                    creator_slug=affilate_creator_slug,
                    affilated_user=user,
                    percent=percent
                )

                # save relation
                new_one_relation = AffilateRelation()
                new_one_relation.creator_id = form_affilate_creator
                new_one_relation.affilated_user = user
                new_one_relation.code = None
                new_one_relation.save()

                return redirect('index')

            except Exception:

                messages.error(request, 'Кажется, некорректно введён Slug. Если же верно, пожалуйста, напишите Диме. ')

    how_much_affilate = None
    aff_money = None
    affilate_creator_slug = None
    percent = None

    if AffilateInfo.objects.filter(user_id=user).exists():

        aff_money = AffilateInfo.objects.get(user_id=user).sum

    if AffilateRelation.objects.filter(affilated_user=user).exists():

        affilate_creator = AffilateRelation.objects.filter(affilated_user=user).first().creator_id
        affilate_creator_slug = affilate_creator.slug

        percent = AffilateInfo.objects.filter(user_id=affilate_creator).first().percent

    if AffilateLogs.objects.filter(creator_id=user).exists():

        how_much_affilate = len(AffilateRelation.objects.filter(creator_id=user).all())

    # because of custom HTML form. (why not form=CustomForm(), etc.)
#    request.POST = None

    data = f'tags: {tags}\naffilate_creator_slug: {affilate_creator_slug}\nhow_much_affilate:{how_much_affilate}\naff_money:{aff_money}'

    try:
        MessageToDmitry(data=f'{data}.').send_message()
    except:
        pass

    return render(request, "users/profile.html", {
        "user": user,
        "intro": intro,
        "projects": projects,
        "badges": badges,
        "tags": tags,
        "active_tags": active_tags,
        "achievements": [ua.achievement for ua in achievements],
        "expertises": expertises,
        "comments": comments[:3],
        "comments_total": comments.count(),
        "posts": posts[:15],
        "posts_total": posts.count(),
        "similarity": similarity,
        "friend": friend,
        "muted": muted,
        'random_coffee_status': random_coffee_status,
        'affilate_creator': affilate_creator_slug,
        'percent': percent,
        'how_much_affilate': how_much_affilate,
        'aff_money': aff_money
    },
        messages)


@auth_required
def profile_comments(request, user_slug):
    if user_slug == "me":
        return redirect("profile_comments", request.me.slug, permanent=False)

    user = get_object_or_404(User, slug=user_slug)

    comments = Comment.visible_objects()\
        .filter(author=user, post__is_visible=True)\
        .order_by("-created_at")\
        .select_related("post")

    return render(request, "users/profile/comments.html", {
        "user": user,
        "comments": paginate(request, comments, settings.PROFILE_COMMENTS_PAGE_SIZE),
    })


@auth_required
def profile_posts(request, user_slug):
    if user_slug == "me":
        return redirect("profile_posts", request.me.slug, permanent=False)

    user = get_object_or_404(User, slug=user_slug)

    posts = Post.objects_for_user(request.me) \
        .filter(author=user, is_visible=True) \
        .exclude(type__in=[Post.TYPE_INTRO, Post.TYPE_PROJECT, Post.TYPE_WEEKLY_DIGEST]) \
        .order_by("-published_at")

    return render(request, "users/profile/posts.html", {
        "user": user,
        "posts": paginate(request, posts, settings.PROFILE_POSTS_PAGE_SIZE),
    })


@auth_required
def profile_badges(request, user_slug):
    if user_slug == "me":
        return redirect("profile_badges", request.me.slug, permanent=False)

    user = get_object_or_404(User, slug=user_slug)

    badges = UserBadge.user_badges(user)

    return render(request, "users/profile/badges.html", {
        "user": user,
        "badges": paginate(request, badges, settings.PROFILE_BADGES_PAGE_SIZE),
    })


@auth_required
@ajax_request
def toggle_tag(request, tag_code):
    if request.method != "POST":
        raise Http404()

    tag = get_object_or_404(Tag, code=tag_code)

    user_tag, is_created = UserTag.objects.get_or_create(
        user=request.me, tag=tag, defaults=dict(name=tag.name)
    )

    if not is_created:
        user_tag.delete()

    SearchIndex.update_user_tags(request.me)

    return {
        "status": "created" if is_created else "deleted",
        "tag": {"code": tag.code, "name": tag.name, "color": tag.color},
    }


@auth_required
@ajax_request
def add_expertise(request):
    if request.method == "POST":
        form = ExpertiseForm(request.POST)
        if form.is_valid():
            user_expertise = form.save(commit=False)
            user_expertise.user = request.me
            UserExpertise.objects.filter(
                user=request.me, expertise=user_expertise.expertise
            ).delete()
            user_expertise.save()

            return {
                "status": "created",
                "expertise": {
                    "name": user_expertise.name,
                    "expertise": user_expertise.expertise,
                    "value": user_expertise.value,
                },
            }

    return {"status": "ok"}


@auth_required
@ajax_request
def delete_expertise(request, expertise):
    if request.method == "POST":
        UserExpertise.objects.filter(user=request.me, expertise=expertise).delete()

        return {
            "status": "deleted",
            "expertise": {
                "expertise": expertise,
            },
        }

    return {"status": "ok"}

@auth_required
def random_coffee(request, user_slug):

    user = User.objects.get(slug=user_slug)

    # if out bot doesn't know user

    if user.telegram_id is None:
        tg_data = 'no telegram_id'
        form = CoffeeForm()

    # if user already earlier saved data in Random Coffee model

    elif RandomCoffee.objects.filter(user=user).exists():

        random_string = RandomCoffee.objects.get(user=user)
        form = CoffeeForm(instance=random_string)

        # if user didn't write his tg_link

        if not random_string.random_coffee_tg_link:
            tg_data = user.telegram_data['username']
        else:
            tg_data = random_string.random_coffee_tg_link

    # if user didn't saved data earlier

    else:
        tg_data = user.telegram_data['username']
        random_string = RandomCoffee()
        random_string.random_coffee_tg_link
        random_string.user = user
        form = CoffeeForm(instance=random_string)

    if request.method == 'POST':

        form = CoffeeForm(request.POST)

        previous_coffee_status = random_string.random_coffee_is

        if form.is_valid():
            random_string.random_coffee_is = form.cleaned_data['random_coffee_is']
            random_string.random_coffee_tg_link = form.cleaned_data['random_coffee_tg_link']

       # that needs changes
        if random_string.random_coffee_is is True and previous_coffee_status is False:

            custom_message = TelegramCustomMessage(
                user=user,
                string_for_bot=text_for_new_user
            )
            custom_message.send_message()
            custom_message.send_count_to_dmitry(type_=f'Новый юзер в рандом кофе: {user.slug}')

        if 'https://t.me/' in random_string.random_coffee_tg_link:
            random_string.random_coffee_tg_link = random_string.random_coffee_tg_link.replace('https://t.me/', '@')

        if random_string.random_coffee_is is True:
            random_string.set_activation_coffee_time()

        random_string.save()
        return redirect('/')

    if tg_data is not None and 'https://t.me/' in tg_data:
        tg_data = tg_data.replace('https://t.me/', '@')

    if tg_data is None:
        tg_data = 'Похоже, твой username скрыт в настройках Telegram'

    return render(request, 'users/profile/random_coffee.html', {
        'form': form,
        'user_slug': user_slug,
        'tg_data': tg_data
    })
