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

@auth_required
def show_helpfullness_list(request):
    list_of_helpfull = DayHelpfulness.objects.all()
    return render(request, 'message/helpfullness_list.html', {'messages': list_of_helpfull})

@auth_required
def create_day_helpfullness(request, id=None, is_archived=False):
    if request.method == 'POST':
        if "Отправить тест Алексею" in request.POST:
            user = User.objects.get(slug='romashovdmitryo')
            if request.POST['image_url'] != '':
                custom_message = TelegramCustomMessage(
                    user=user,
                    photo=request.POST['image_url'],
                    string_for_bot=None
                )
                custom_message.send_message()
            custom_message = TelegramCustomMessage(
                user=user,
                string_for_bot=request.POST['text']
            )
            custom_message.send_message()
            custom_message.send_count_to_dmitry()

        if "Сохранить как черновик" in request.POST:
            is_archived = True
        # if modify
        if id:
            obj = DayHelpfulness.objects.get(id=id)
            obj.is_archived = is_archived
            form = CreateDayHelpfullness(request.POST, instance=obj)
            if form.is_valid():
                form.save()
            return redirect('show_helpfullness_list')
        # if new message
        form = CreateDayHelpfullness(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.is_archived=is_archived
            instance.save()
        return redirect('show_helpfullness_list')
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