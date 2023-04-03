# import Django packages
from django.shortcuts import render, redirect, get_object_or_404
from django.http.response import HttpResponse
from django.contrib import messages

# import Models and forms
from telegramessage.models import DayHelpfulness
from telegramessage.forms import CreateDayHelpfullness
from users.models.user import User

# import auth decorators
from auth.helpers import auth_required

# import for sending message in Telegram
from bot.sending_message import TelegramCustomMessage

# import Python packages
import re

# import config data
from club.settings import TG_DEVELOPER_DMITRY, TG_ALEX

def construct_message(text):

    '''add UTM to links in text'''

    new_string = ''
    while 'https://sorokin' in text:
        x = re.search(r'https://sorokin[\w\d\=\:\/\.\?\-\&\%\;]+', text)
        start = x.start()
        finish = x.end()
        y = x.group()
        new_string = new_string + text[0:start] + y + '?utm_source=private_bot_newsletter'
        text = text[finish:]
    new_string += text
    return new_string

@auth_required
def show_helpfullness_list(request):
    list_of_helpfull = DayHelpfulness.objects.all()
    return render(request, 'message/helpfullness_list.html', {'messages': list_of_helpfull})

@auth_required
def create_day_helpfullness(request, id=None, is_archived=False):

    if request.method == 'POST':

        # if sending message to Alex for checking

        if "Отправить тест Алексею" in request.POST:

            dmitry = User.objects.get(telegram_id=TG_DEVELOPER_DMITRY)
            alex = User.objects.get(slug=TG_ALEX)
            users = [dmitry, alex]

            image_url = request.POST['image_url'].replace(" ", '')
            string_for_bot = construct_message(request.POST['text'])

            for user in users:

                if image_url != '':

                    custom_message = TelegramCustomMessage(
                        user=user,
                        photo=image_url,
                        string_for_bot=string_for_bot
                    )

                    custom_message.send_photo()

                else:

                    custom_message = TelegramCustomMessage(
                        user=user,
                        string_for_bot=string_for_bot
                    )

                    custom_message.send_message()

            custom_message.send_count_to_dmitry()

        if "Сохранить как черновик" in request.POST:
            is_archived = True

        # if modify message

        if id:
            obj = DayHelpfulness.objects.get(id=id)
            obj.is_archived = is_archived
            form = CreateDayHelpfullness(request.POST, instance=obj)
            if form.is_valid():
                form.save()
            else:
                return render(
                    request, 'message/create_day_helpfullness.html',
                    {
                        'form': form,
                        'validation_errors': form.errors
                    }
                )
            return redirect('show_helpfullness_list')

        # if new message

        form = CreateDayHelpfullness(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.is_archived = is_archived
            instance.save()
        else:
            return render(
                request, 'message/create_day_helpfullness.html',
                {
                    'form': form,
                    'validation_errors': form.errors
                }
            )
        return redirect('show_helpfullness_list')

    # if there is not post method

    if id is None:

        form = CreateDayHelpfullness()
        return render(request, 'message/create_day_helpfullness.html', {'form': form})

    else:

        obj = get_object_or_404(DayHelpfulness, id=id)
        form = CreateDayHelpfullness(instance=obj)

    return render(request, 'message/create_day_helpfullness.html', {'form': form, 'id': obj.id})

@auth_required
def delete_day_helpfullness(request, id):
    obj = DayHelpfulness.objects.get(id=id)
    obj.delete()
    return redirect('show_helpfullness_list')
