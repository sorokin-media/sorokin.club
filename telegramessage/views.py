from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from django.contrib import messages
import uuid

from .forms import CreateMessage
from .models import TelegramMesage

from club import settings

import telegram
from telegram import Update, ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

# 204349098

def get_data_for_html(tgmessage):
    initial_dict = {
        'days': tgmessage.time_delay.day,
        'hours': tgmessage.time_delay.hour,
        'minutes': tgmessage.time_delay
    }
    form = CreateMessage(instance=tgmessage)
    return form

def show_telegram_messages(request):
    request.session['status'] = 'create'
    if TelegramMesage.objects.all().exists():
        tgmessages = TelegramMesage.objects.all().order_by('days', 'hours', 'minutes')
        return render(request, 'message/show_messages.html', {'messages': tgmessages})
    else:
        return render(request, 'message/show_messages.html')

def create_message_helper(days, hours, minutes,
                          name, text, is_finish_of_queue,
                          is_archived, image_url, test):
    new_message = TelegramMesage()
    new_message.save_data(days=days, hours=hours, minutes=minutes,
                          name=name, text=text, is_finish_of_queue=is_finish_of_queue,
                          is_archived=is_archived, image_url=image_url)
    if test == 'on':
        bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
        if image_url is not None:
            bot.send_photo(
                chat_id=204349098,
                photo=image_url
            )
        bot.send_message(chat_id=204349098,
                         text=f'Паша, тебе сообщение на проверку!\n\nНазвание сообщения: {name}\n\nТекст сообщения: {text}',
                         )

def check_uniqie_helper(name, id):
    # True if not unique, else False
    name_list = list(TelegramMesage.objects.values_list('name', flat=True).distinct())
    id_in_db = TelegramMesage.objects.filter(name=name).exists()  # если есть такой
    return True if name in name_list and not id_in_db else False

# this view create message ot modify
# depending on session['status']
def create_telegram_message(request):
    if request.method == 'POST':
        # get data from form
        test = str(request.POST.get('test'))
        days = int(request.POST.get('days'))
        hours = int(request.POST.get('hours'))
        minutes = int(request.POST.get('minutes'))
        name = request.POST.get('name')
        text = request.POST.get('text')
        is_finish_of_queue = request.POST.get('is_finish_of_queue')
        image_url = request.POST.get('image_url')
        is_archived = request.POST.get('is_archived')
        # modify word
        if request.session['status'] == 'modify':
            id = request.session['id']
            # if there is similar name in DB already
            if check_uniqie_helper(name, id) is True:
                tgmessage = TelegramMesage.objects.filter(id=id).first()
                form = get_data_for_html(tgmessage)
                messages.error(request, "Сообщение с таким названием уже имеется")
                return render(request, 'message/create_message.html', {"form": form}, messages)
            else:
                message = TelegramMesage.objects.get(id=id)
                message.save_data(days=days, hours=hours, minutes=minutes,
                                  name=name, text=text, is_finish_of_queue=is_finish_of_queue,
                                  is_archived=is_archived, image_url=image_url)
                del request.session['id']
                request.session['status'] = 'create'
                return redirect('show_telegram_messages')
        elif request.session['status'] == 'create':
            create_message_helper(days=days, hours=hours, minutes=minutes,
                                  name=name, text=text, is_finish_of_queue=is_finish_of_queue,
                                  is_archived=is_archived, image_url=image_url, test=test)
            tgmessages = TelegramMesage.objects.all()
            return redirect('show_telegram_messages')

    form = CreateMessage
    return render(request, 'message/create_message.html', {"form": form})
    # create word


def modify_telegram_message(request, message_id):
    tgmessage = TelegramMesage.objects.filter(id=message_id).first()
    request.session['id'] = str(message_id)
    request.session['status'] = 'modify'
    form = CreateMessage(instance=tgmessage)
    return render(request, 'message/create_message.html', {"form": form})

def delete_telegram_message(request):
    id = request.session['id']
    TelegramMesage.objects.filter(id=id).delete()
    del request.session['id']
    return redirect('show_telegram_messages')
