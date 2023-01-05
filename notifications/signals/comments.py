from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task

from club import settings
from notifications.telegram.common import Chat, send_telegram_message, render_html_message, CLUB_ONLINE, ADMIN_CHAT
from comments.models import Comment
from common.regexp import USERNAME_RE
from posts.models.subscriptions import PostSubscription
from users.models.friends import Friend
from users.models.mute import Muted
from users.models.user import User
from django.template import loader, TemplateDoesNotExist
from notifications.email.sender import send_club_email


@receiver(post_save, sender=Comment)
def create_or_update_comment(sender, instance, created, **kwargs):
    if not created:
        return None  # we're not interested in comment updates

    async_task(async_create_or_update_comment, instance)

def mute_check(user_from, user_to):
    return Muted.is_muted(
        user_from=user_from,
        user_to=user_to
    )

def async_create_or_update_comment(comment):
    notified_user_ids = set()

    # notify post subscribers
    post_subscribers = PostSubscription.post_subscribers(comment.post)
    for post_subscriber in post_subscribers:
        if post_subscriber.user.telegram_id and comment.author != post_subscriber.user:
            # respect subscription type (i.e. all comments vs top level only)
            if post_subscriber.type == PostSubscription.TYPE_ALL_COMMENTS \
                    or (post_subscriber.type == PostSubscription.TYPE_TOP_LEVEL_ONLY and not comment.reply_to_id):
                if mute_check(user_from=post_subscriber.user, user_to=comment.author):
                    send_telegram_message(
                        chat=Chat(id=post_subscriber.user.telegram_id),
                        text=render_html_message("comment_to_post.html", comment=comment),
                    )
                    notified_user_ids.add(post_subscriber.user.id)

        else:
            if comment.author != post_subscriber.user:
                if post_subscriber.type == PostSubscription.TYPE_ALL_COMMENTS \
                        or (post_subscriber.type == PostSubscription.TYPE_TOP_LEVEL_ONLY and not comment.reply_to_id):
                    renewal_template = loader.get_template("emails/comment_to_post_email.html")
                    send_club_email(
                        recipient=post_subscriber.user.email,
                        subject=f"Новый коммент к посту!",
                        html=renewal_template.render({"comment": comment}),
                        tags=["comment"]
                    )
    # notify thread author on reply (note: do not notify yourself)
    if comment.reply_to:
        if mute_check(user_from=comment.reply_to.author, user_to=comment.author):
            thread_author = comment.reply_to.author
            if thread_author.telegram_id:
                if comment.author != thread_author and thread_author.id not in notified_user_ids:
                    send_telegram_message(
                        chat=Chat(id=thread_author.telegram_id),
                        text=render_html_message("comment_to_thread.html", comment=comment),
                    )
                    notified_user_ids.add(thread_author.id)
            else:
                if comment.author != thread_author and thread_author.id not in notified_user_ids:
                    renewal_template = loader.get_template("emails/comment_to_thread_email.html")
                    send_club_email(
                        recipient=thread_author.email,
                        subject=f"Новый реплай к вашему комментарию!",
                        html=renewal_template.render({"comment": comment}),
                        tags=["comment"]
                    )
                    notified_user_ids.add(thread_author.id)

    # post top level comments to online channel
    if not comment.reply_to and comment.post.is_visible and comment.post.is_visible_in_feeds:
        send_telegram_message(
            chat=CLUB_ONLINE,
            text=render_html_message("comment_to_post.html", comment=comment),
        )

    # notify friends about your comments (not replies)
    if not comment.reply_to:
        friends = Friend.friends_for_user(comment.author)
        for friend in friends:
            if friend.user_from.telegram_id \
                    and friend.is_subscribed_to_comments \
                    and friend.user_from.id not in notified_user_ids:
                send_telegram_message(
                    chat=Chat(id=friend.user_from.telegram_id),
                    text=render_html_message("friend_comment.html", comment=comment),
                )
                notified_user_ids.add(friend.user_from.id)

    # parse @nicknames and notify their
    for username in USERNAME_RE.findall(comment.text):
        if username == settings.MODERATOR_USERNAME:
            send_telegram_message(
                chat=ADMIN_CHAT,
                text=render_html_message("moderator_mention.html", comment=comment),
            )
            continue

        user = User.objects.filter(slug=username).first()
        is_muted = Muted.objects.filter(user_from=user, user_to=comment.author).exists()
        if is_muted:
            continue

        if user and user.telegram_id and user.id not in notified_user_ids:
            send_telegram_message(
                chat=Chat(id=user.telegram_id),
                text=render_html_message("comment_mention.html", comment=comment),
            )
            notified_user_ids.add(user.id)
