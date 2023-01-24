from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from django.contrib import messages
import uuid

from .forms import CreateMessage
from .models import TelegramMesage

from club import settings

from auth.helpers import auth_required

import telegram
from telegram import Update, ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

# 204349098
@auth_required
def show_telegram_messages(request):
    request.session['status'] = 'create'
    if TelegramMesage.objects.all().exists():
        tgmessages = TelegramMesage.objects.all().order_by('days', 'hours', 'minutes')
        return render(request, 'message/show_messages.html', {'messages': tgmessages})
    else:
        return render(request, 'message/show_messages.html')

@auth_required
def create_message_helper(days, hours, minutes,
                          name, text, is_finish_of_queue,
                          is_archived, image_url, test):
    new_message = TelegramMesage()
    new_message.save_data(days=days, hours=hours, minutes=minutes,
                          name=name, text=text, is_finish_of_queue=is_finish_of_queue,
                          is_archived=is_archived, image_url=image_url)
    if test == 'on':
        bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
        bot.send_message(chat_id=204349098,
                         text=text)

# None when create
def check_uniqie_helper(name, id):
    name_list = list(TelegramMesage.objects.values_list('name', flat=True).distinct())
    if id is None and name in name_list:
        return True
    id_in_db = TelegramMesage.objects.filter(name=name).exists()  # если есть такой
    print(f'\n\nname in name_list: {name in name_list}\n\n')
    # True if not unique, else False
    print(f'\n\nid in db: {id_in_db}\n\n')
    return True if name in name_list and not id_in_db else False

# this view create message ot modify
# depending on session['status']
@auth_required
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
                form = CreateMessage(request.POST)
                messages.error(request, "Сообщение с таким названием уже имеется")
                return render(request, 'message/create_message.html', {"form": form, "status": "modify"}, messages)
            else:
                message = TelegramMesage.objects.get(id=id)
                message.save_data(days=days, hours=hours, minutes=minutes,
                                  name=name, text=text, is_finish_of_queue=is_finish_of_queue,
                                  is_archived=is_archived, image_url=image_url)
                del request.session['id']
                request.session['status'] = 'create'
                return redirect('show_telegram_messages')
        # if we create new message
        elif request.session['status'] == 'create':
            if check_uniqie_helper(name, id=None) is True:
                form = CreateMessage(request.POST)
                messages.error(request, "Сообщение с таким названием уже имеется")
                return render(request, 'message/create_message.html', {"form": form, "status": "create"}, messages)
            create_message_helper(days=days, hours=hours, minutes=minutes,
                                  name=name, text=text, is_finish_of_queue=is_finish_of_queue,
                                  is_archived=is_archived, image_url=image_url, test=test)
            tgmessages = TelegramMesage.objects.all()
            return redirect('show_telegram_messages')
    form = CreateMessage
    return render(request, 'message/create_message.html', {"form": form})

@auth_required
def modify_telegram_message(request, message_id):
    tgmessage = TelegramMesage.objects.filter(id=message_id).first()
    request.session['id'] = str(message_id)
    request.session['status'] = 'modify'
    form = CreateMessage(instance=tgmessage)
    return render(request, 'message/create_message.html', {"form": form, "status": "modify"})

@auth_required
def delete_telegram_message(request):
    id = request.session['id']
    TelegramMesage.objects.filter(id=id).delete()
    del request.session['id']
    return redirect('show_telegram_messages')
