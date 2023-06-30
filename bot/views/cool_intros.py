# import Django packages
from django.shortcuts import render, redirect, get_object_or_404

# import Forms and Models
from bot.forms import CoolIntroForm
from bot.models.cool_intros import CoolIntro
from users.models.user import User

# import config data
from club.settings import TG_ALEX, TG_DEVELOPER_DMITRY, TG_NUTA

# import class for sending message in Telegram
from bot.sending_message import TelegramCustomMessage, MessageToDmitry

# import auth decorators
from auth.helpers import auth_required

# Telegram imports
import telegram
from telegram import Update, ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

# Python imports
import re

# impotr models
from bot.models.cool_intros import CoolIntro

def construct_message(text):

    '''add UTM to links in text'''

    new_string = ''
    while 'https://sorokin' in text:
        x = re.search(r'https://sorokin[\w\d\=\:\/\.\?\-\&\%\;]+', text)
        start = x.start()
        finish = x.end()
        y = x.group()
        new_string = new_string + text[0:start] + y + '?utm_source=private_bot_cool_intros'
        text = text[finish:]
    new_string += text
    return new_string


@auth_required
def cool_intros(request):
    cool_intros = CoolIntro.objects.all()
    return render(request, 'message/cool_intros.html', {'messages': cool_intros})

@auth_required
def create_cool_intro(request, id=None, is_archived=False):

    if request.method == 'POST':

        # if sending message to Alex for checking

        if "Отправить тест" in request.POST:

            dmitry = User.objects.get(telegram_id=TG_DEVELOPER_DMITRY)
    
            users = [
                dmitry,
                User.objects.get(id=request.POST['test_user'])
            ]

            image_url = request.POST['image_url'].replace(" ", '')
            string_for_bot = construct_message(request.POST['text'])

            for user in users:

                if image_url is not None and image_url != '':

                    custom_message = TelegramCustomMessage(
                        user=user,
                        photo=image_url,
                        string_for_bot=''
                    )

                    custom_message.send_photo()

                    custom_message = TelegramCustomMessage(
                        user=user,
                        string_for_bot=string_for_bot
                    )

                    custom_message.send_message()

                else:

                    custom_message = TelegramCustomMessage(
                        user=user,
                        string_for_bot=string_for_bot
                    )

                    custom_message.send_message()

            custom_message.send_count_to_dmitry()
            return redirect('create_cool_intro', id)
            
        if "Сохранить как черновик" in request.POST:
            is_archived = True

        # if modify message

        if id:
            obj = CoolIntro.objects.get(id=id)
            obj.is_archived = is_archived
            form = CoolIntroForm(request.POST, instance=obj)
            if form.is_valid():
                form.save()
            else:
                return render(
                    request, 'message/create_cool_intro.html',
                    {
                        'form': form,
                        'validation_errors': form.errors
                    }
                )
            return redirect('cool_intros')

        # if new message

        form = CoolIntroForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.is_archived = is_archived
            instance.save()
        else:
            return render(
                request, 'message/create_cool_intro.html',
                {
                    'form': form,
                    'validation_errors': form.errors
                }
            )
        return redirect('cool_intros')

    # if there is not post method

    if id is None:

        form = CoolIntroForm()
        return render(request, 'message/create_cool_intro.html', {'form': form})

    else:

        obj = get_object_or_404(CoolIntro, id=id)
        form = CoolIntroForm(instance=obj)

    return render(request, 'message/create_cool_intro.html', {'form': form, 'id': obj.id})

@auth_required
def delete_cool_intro(request, id):
    obj = CoolIntro.objects.get(id=id)
    obj.delete()
    return redirect('cool_intros')
