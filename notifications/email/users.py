from django.template import loader, TemplateDoesNotExist

from auth.models import Code
from bot.handlers.common import UserRejectReason
from users.models.user import User
from payments.models import Payment

# for logging bugs
from bot.sending_message import TelegramCustomMessage, MessageToDmitry

from notifications.email.sender import Email

def send_payed_email(user: User):
    payment_template = loader.get_template("emails/payment_done.html")
    email = Email(
        html=payment_template.render({"user": user}),
        email=user.email,
        subject="Оплата прошла"
    )
    email.prepare_email()
    email.send()


def send_payed_email_single(email: str):
    payment_template = loader.get_template("emails/payment_done_link.html")
    email = Email(
        html=payment_template.render({"email": email}),
        email=email,
        subject="Оплата прошла"
    )
    email.prepare_email()
    email.send()


def send_registration_email(user: User):
    registration_template = loader.get_template("emails/registration.html")
    email = Email(
        html=registration_template.render({"user": user}),
        email=user.email,
        subject="Ваше приглашение 🪪"
    )
    email.prepare_email()
    email.send()


def send_renewal_email(user: User):
    renewal_template = loader.get_template("emails/renewal.html")
    email = Email(
        html=renewal_template.render({"user": user}),
        email=user.email,
        subject="Ваша подписка стала еще длинее!"
    )
    email.prepare_email()
    email.send()


def send_welcome_drink(user: User):
    welcome_drink_template = loader.get_template("emails/welcome.html")
    email = Email(
        html=welcome_drink_template.render({"user": user}),
        email=user.email,
        subject="Велком дринк 🍸"
    )
    email.prepare_email()
    email.send()


def send_user_rejected_email(user: User, reason: UserRejectReason):
    try:
        rejected_template = loader.get_template(f"emails/rejected/{reason.value}.html")
    except TemplateDoesNotExist:
        rejected_template = loader.get_template(f"emails/rejected/intro.html")

    email = Email(
        html=rejected_template.render({"user": user}),
        email=user.email,
        subject="😕 Пока нет"
    )
    email.prepare_email()
    email.send()


def send_auth_email(user: User, code: Code):
    auth_template = loader.get_template("emails/auth.html")
    email = Email(
        html=auth_template.render({"user": user, "code": code}),
        email=user.email,
        subject=f"{code.code} — ваш код для входа"
    )
    email.prepare_email()
    email.send()
    

def send_unmoderated_email(user: User):
    rejected_template = loader.get_template("emails/unmoderated.html")
    email = Email(
        html=rejected_template.render({"user": user}),
        email=user.email,
        subject=f"😱 Вас размодерировали"
    )
    email.prepare_email()
    email.send()


def send_banned_email(user: User, days: int, reason: str):
    if not user.is_banned or not days:
        return  # not banned oO
    banned_template = loader.get_template("emails/banned.html")

    email = Email(
        html=banned_template.render({
            "user": user,
            "days": days,
            "reason": reason,
        }),
        email=user.email,
        subject=f"💩 Вас забанили"
    )
    email.prepare_email()
    email.send()


def send_subscribe_8_email(user: User, sum: int):
    sub_template = loader.get_template("emails/subscriptions_8.html")
    email = Email(
        html=sub_template.render({
            "user": user,
            "sum": sum
        }),
        email=user.email,
        subject=f"Оплата подписки"
    )
    email.prepare_email()
    email.send()


def couldnd_withdraw_money_email(user: User):
    sub_template = loader.get_template("emails/withdraw_money.html")

    email = Email(
        html=sub_template.render({
            "user": user,
        }),
        email=user.email,
        subject="Оплата подписки"
    )
    email.prepare_email()
    email.send()


def cancel_subscribe_user_email(user: User):
    sub_template = loader.get_template("emails/cancel_subscribe.html")
    email = Email(
        html=sub_template.render({
            "user": user,
        }),
        email=user.email,
        subject="Оплата подписки"
    )
    email.prepare_email()
    email.send()


def payment_reminder_5_email(user: User):
    sub_template = loader.get_template("emails/payment_reminder_5.html")
    email = Email(
        html=sub_template.render({
            "user": user,
        }),
        email=user.email,
        subject="Заканчиваются дни в Сорокин Клубе 😿"
    )
    email.prepare_email()
    email.send()


def payment_reminder_3_email(user: User):
    sub_template = loader.get_template("emails/payment_reminder_3.html")

    email = Email(
        html=sub_template.render({
            "user": user,
        }),
        email=user.email,
        subject="Осталось всего три дня Сорокин Клубе 😿"
    )
    email.prepare_email()
    email.send()


def payment_reminder_1_email(user: User):
    sub_template = loader.get_template("emails/payment_reminder_1.html")

    email = Email(
        html=sub_template.render({
            "user": user,
        }),
        email=user.email,
        subject="Завтра заканчивается участие в Сорокин Клубе 😿"
    )
    email.prepare_email()
    email.send()


def send_ping_email(user: User, message: str):
    ping_template = loader.get_template("emails/ping.html")
    email = Email(
        html=ping_template.render({"message": message}),
        email=user.email,
        subject="👋 Вам письмо"
    )
    email.prepare_email()
    email.send()


def send_data_archive_ready_email(user: User, url: str):
    auth_template = loader.get_template("emails/data_archive_ready.html")
    email = Email(
        html=auth_template.render({"user": user, "url": url}),
        email=user.email,
        subject="💽 Ваш архив с данными готов"
    )
    email.prepare_email()
    email.send()


def send_delete_account_request_email(user: User, code: Code):
    auth_template = loader.get_template("emails/delete_account_request.html")
    email = Email(
        html=auth_template.render({"user": user, "code": code}),
        email=user.email,
        subject="🧨 Код для удаления аккаунта"
    )
    email.prepare_email()
    email.send()


def send_delete_account_confirm_email(user: User):
    auth_template = loader.get_template("emails/delete_account_confirm.html")
    email = Email(
        html=auth_template.render({"user": user}),
        email=user.email,
        subject="✌️ Ваш аккаунт в Клубе будет удалён"
    )
    email.prepare_email()
    email.send()
