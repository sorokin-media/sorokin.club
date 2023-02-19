from collections import namedtuple

from django import template
from django.utils.safestring import mark_safe

from club import settings
from common.markdown.markdown import markdown_text
from bs4 import BeautifulSoup
import base64

register = template.Library()

TreeComment = namedtuple("TreeComment", ["comment", "replies"])


@register.filter()
def comment_tree(comments):
    comments = list(comments)  # in case if it's a queryset
    tree = []

    # build reply tree (3 levels)
    for comment in comments:
        # find 1st level comments
        if not comment.reply_to:
            replies = []
            for reply in sorted(comments, key=lambda c: c.created_at):
                # 2nd level replies
                if reply.reply_to_id == comment.id:
                    replies.append(
                        TreeComment(
                            comment=reply,
                            replies=sorted(  # 3rd level replies
                                [c for c in comments if c.reply_to_id == reply.id],
                                key=lambda c: c.created_at
                            )
                        )
                    )
            tree.append(
                TreeComment(
                    comment=comment,
                    replies=replies
                )
            )

    # move pinned comments to the top
    tree = sorted(tree, key=lambda c: c.comment.is_pinned, reverse=True)

    return tree


@register.simple_tag(takes_context=True)
def render_comment(context, comment):
    if comment.is_deleted:
        if comment.deleted_by == comment.author_id:
            by_who = " его автором"
        elif comment.deleted_by == comment.post.author_id:
            by_who = " автором поста"
        else:
            by_who = " модератором"

        return mark_safe(
            f"""<p class="comment-text-deleted">😱 Комментарий удален{by_who}...</p>"""
        )

    if not comment.html or settings.DEBUG:
        new_html = markdown_text(comment.text)
        if new_html != comment.html:
            # to not flood into history
            comment.html = new_html
            comment.save()

    soup = BeautifulSoup(comment.html, 'html.parser')
    rows = soup.find_all('a')
    # тест заливки
    for link in rows:
        flag_link = True
        href_link = link.get('href')
        href_text = link.get_text()
        if 'http' not in href_link:
            flag_link = False
        for setting_link in settings.LINKS_WHITE_LIST:
            if setting_link in href_link:
                flag_link = False

        if flag_link:
            href_in_byte = href_link.encode("UTF-8")
            href_link_encode = base64.b64encode(href_in_byte)
            href_in_string_decode = href_link_encode.decode("UTF-8")
            new_tag_span = soup.new_tag('span', attrs={'class': 'hlink', 'data-href': href_in_string_decode})
            new_tag_span.string = href_text
            link.replace_with(new_tag_span)

    return mark_safe(str(soup) or "")
