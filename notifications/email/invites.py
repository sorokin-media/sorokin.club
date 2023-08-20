from django.template import loader

from users.models.user import User

from notifications.email.sender import Email

def send_invited_email(from_user: User, to_user: User):
    invite_template = loader.get_template("emails/invited.html")
    email = Email(
        html=invite_template.render({"from_user": from_user, "to_user": to_user}),
        email=to_user.email,
        subject="🚀 Вас пригласили в Клуб"
    )
    email.prepare_email()
    email.send()


def send_invite_renewed_email(from_user: User, to_user: User):
    invite_template = loader.get_template("emails/invite_renewed.html")
    email = Email(
        html=invite_template.render({"from_user": from_user, "to_user": to_user}),
        email=to_user.email,
        subject="🚀 Вам оплатили аккаунт в Клубе"
    )
    email.prepare_email()
    email.send()


def send_invite_confirmation(from_user: User, to_user: User):
    invite_template = loader.get_template("emails/invite_confirm.html")
    email = Email(
        html=invite_template.render({"from_user": from_user, "to_user": to_user}),
        email=from_user.email,
        subject=f"👍 Вы оплатили для '{to_user.email}' аккаунт в Клубе"
    )
    email.prepare_email()
    email.send()