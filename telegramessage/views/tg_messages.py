# import Django packages
from django.shortcuts import render, redirect
from django.contrib import messages

# import Forms and Models
from telegramessage.forms import CreateMessage
from telegramessage.models import TelegramMesage
from users.models.user import User

# import config data
from club.settings import TG_ALEX, TG_DEVELOPER_DMITRY

# import class for sending message in Telegram
from bot.sending_message import TelegramCustomMessage, MessageToDmitry

# import auth decorators
from auth.helpers import auth_required

# Telegram imports
import telegram
from telegram import Update, ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext


@auth_required
def show_telegram_messages(request):
    if TelegramMesage.objects.all().exists():
        tgmessages = TelegramMesage.objects.all().order_by('days', 'hours', 'minutes')
        return render(request, 'message/show_messages.html', {'messages': tgmessages})
    else:
        return render(request, 'message/show_messages.html')

# None when create
def check_uniqie_helper(name, is_finish_of_queue, id=None):

    name_list = list(TelegramMesage.objects.values_list('name', flat=True).distinct())

    MessageToDmitry(data=f'name_list: {str(name_list)}').send_message()

    MessageToDmitry(data=f'NAME: {name}').send_message()

    check = name in name_list
    MessageToDmitry(data=f'Name in Name list? {check}').send_message()

    # is there name in list of message's name that already exist
    if id is None and name in name_list:

        MessageToDmitry(data='id is not none in unique helper')
        MessageToDmitry(data=f'type of id: {type(id)}')

        return 'Please, modify name of message'

    id_in_db = TelegramMesage.objects.filter(name=name).exists()

    MessageToDmitry(data=f'id in db: {id_in_db}')

    # True if not unique, else False
    if name in name_list and not id_in_db:
        return 'Please, modify name of message'

    if is_finish_of_queue == 'True':

        MessageToDmitry(data='finish if queue = True').send_message()

        if TelegramMesage.objects.filter(is_finish_of_queue=True).exists():
            MessageToDmitry(data='come to text of error').send_message()
            return 'The queue already has an end'

    MessageToDmitry(data='return true').send_message()
    return True

def save_data_helper(request, message, days, hours, minutes, name, text,
                     is_finish_of_queue, image_url=''):

    if "Отправить тест Алексею" in request.POST:

        #        tg_id_of_alex = User.objects.get(telegram_id=TG_ALEX)
        #        tg_id_of_dima = User.objects.get(telegram_id=TG_DEVELOPER_DMITRY)
        #        tg_ids = [tg_id_of_alex, tg_id_of_dima]

        # for tests on local
        #fortest = User.objects.filter(slug='dev').first()
        #tg_ids = [fortest]

        # for test on prod by Dmitry
        tg_id_of_dima = User.objects.get(telegram_id=TG_DEVELOPER_DMITRY)
        tg_ids = [tg_id_of_dima]

        for _ in tg_ids:

            if image_url != '':

                custom_message = TelegramCustomMessage(
                    user=_,
                    photo=image_url,
                    string_for_bot=text
                )

                custom_message.send_photo()

            else:

                custom_message = TelegramCustomMessage(
                    user=_,
                    string_for_bot=text
                )

                custom_message.send_message()

        custom_message.send_count_to_dmitry()

        MessageToDmitry(data='AMA HERE BITCH').send_message()

        message.save_data(
            days=days,
            hours=hours,
            minutes=minutes,
            name=name,
            text=text,
            is_finish_of_queue=is_finish_of_queue,
            is_archived=True,
            image_url=image_url
        )

    elif "Сохранить как черновик" in request.POST:
        message.save_data(
            days=days,
            hours=hours,
            minutes=minutes,
            name=name,
            text=text,
            is_finish_of_queue=is_finish_of_queue,
            is_archived=True,
            image_url=image_url
        )

    else:
        message.save_data(
            days=days,
            hours=hours,
            minutes=minutes,
            name=name,
            text=text,
            is_finish_of_queue=is_finish_of_queue,
            is_archived=False,
            image_url=image_url
        )

@auth_required
def create_telegram_message(request, message_id=None):
    if request.method == 'POST':

        MessageToDmitry(data='come here').send_message()

        # get data from form

        days = int(request.POST.get('days'))
        hours = int(request.POST.get('hours'))
        minutes = int(request.POST.get('minutes'))
        name = request.POST.get('name')
        text = request.POST.get('text')
        is_finish_of_queue = request.POST.get('is_finish_of_queue')
        image_url = request.POST.get('image_url')

        # if app modify message

        MessageToDmitry(data='next setp').send_message()

        if message_id is not None:

            MessageToDmitry(data='message id is no None').send_message()

            id = message_id
            # if there is similar name in DB already or duplicate final of queue
            unique_of_message = check_uniqie_helper(name, is_finish_of_queue, id)

            MessageToDmitry(data=f'unique? -> {unique_of_message}').send_message()

            if unique_of_message is not True:

                MessageToDmitry(data='final 1').send_message()

                form = CreateMessage(request.POST)
                MessageToDmitry(data='final 2').send_message()
                messages.error(request, unique_of_message)
                MessageToDmitry(data='final 3').send_message()
                MessageToDmitry(data=f'message_id: {message_id}').send_message()

                return render(
                    request, 'message/create_message.html',
                    {
                        "form": form,
                        "status": "modify",
                        'message_id': message_id
                    },
                    messages
                )

            MessageToDmitry(data='Oooops!').send_message()

            message = TelegramMesage.objects.get(id=id)

            save_data_helper(request=request, message=message, days=days, hours=hours, minutes=minutes,
                             name=name, text=text, is_finish_of_queue=is_finish_of_queue, image_url=image_url)

        # if app create new message

        elif message_id is None:

            # if there is similar name in DB already or duplicate final of queue
            unique_of_message = check_uniqie_helper(name, is_finish_of_queue)

            if unique_of_message is not True:

                form = CreateMessage(request.POST)
                messages.error(request, unique_of_message)
                return render(request, 'message/create_message.html', {"form": form, "status": "create"}, messages)

            message = TelegramMesage()
            save_data_helper(request=request, message=message, days=days, hours=hours, minutes=minutes,
                             name=name, text=text, is_finish_of_queue=is_finish_of_queue)

        return redirect('show_telegram_messages')

    # just open DOM

    form = CreateMessage
    return render(request, 'message/create_message.html', {"form": form})

@auth_required
def modify_telegram_message(request, message_id):
    tgmessage = TelegramMesage.objects.filter(id=message_id).first()
    form = CreateMessage(instance=tgmessage)
    return render(request, 'message/create_message.html', {"form": form,
                                                           "status": "modify",
                                                           'message_id': message_id})

@auth_required
def delete_telegram_message(request, message_id):
    id = message_id
    TelegramMesage.objects.filter(id=id).delete()
    return redirect('show_telegram_messages')
