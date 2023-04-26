import json

from django import template

from users.models.tags import Tag

from datetime import datetime, timedelta
import pytz

register = template.Library()


@register.simple_tag()
def user_tag_images(user):
    tags = user.tags.filter(tag__group=Tag.GROUP_HOBBIES)[:5]
    return " ".join([str(t.name.split(" ", 1)[0]) for t in tags])


@register.simple_tag()
def users_geo_json(users):
    return json.dumps({
        "type": "FeatureCollection",
        "id": "user-markers",
        "features": [{
            "type": "Feature",
            "properties": {
                "id": user.slug,
                "url": f"/user/{user.slug}/",
                "avatar": user.avatar,
            },
            "geometry": {
                "type": "Point",
                "coordinates": user.geo.to_json_coordinates(randomize=True),
            }
        } for user in users if user.geo]
    })

@register.simple_tag()
def active_or_not(user):

    time_zone = pytz.UTC
    now = time_zone.localize(datetime.utcnow())

    x = now < time_zone.localize(user.membership_expires_at)
    y = user.is_banned_until is None
    if not y:
        y = user.is_banned_until < now
    z = user.moderation_status == 'approved'

    return "Активен" if x and y and z else "Не активен"

@register.simple_tag()
def get_amount_from_str(comment):

    print('\nCOME GO GO')

    if 'Bonus Money: ' in comment:

        return comment.replace("Bonus Money: ", "")

    elif 'Bonus Days: ' in comment:

        return comment.replace("Bonus Days: ", "")

@register.simple_tag()
def make_moscow_time(utc_date_time):

    time_zone = pytz.UTC    
    moscow_date_time = time_zone.localize(utc_date_time)
    return moscow_date_time.strftime('%Y-%m-%d')