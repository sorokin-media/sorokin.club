# import Django packages
from django.shortcuts import render, redirect
from django.contrib import messages

# import config data
from club.settings import TG_DEVELOPER_DMITRY

# import Forms and Models
from posts.models.topics import Topic
from posts.forms.compose import CreateTopic

# import class for sending message in Telegram
from bot.sending_message import MessageToDmitry

# import auth decorators
from auth.helpers import auth_required

# Python imports

@auth_required
def show_list_of_rooms(request):
    rooms = Topic.objects.all()
    return render(request, 'posts/compose/topics/show_topic.html', {'rooms': rooms})


def open_form(request):
    return render(request, 'posts/compose/topics/create_topic.html', {"form": CreateTopic()})

@auth_required
def create_topic(request, room_slug=None):

    if request.method == 'POST':

        if room_slug is not None:

            obj = Topic.objects.get(slug=room_slug)
            form = CreateTopic(request.POST, instance=obj)

        else:
                
            form = CreateTopic(request.POST)

        if form.is_valid():

            form.save()
            return redirect('index')

        messages.error(request, form.errors)

        return render(request, 'posts/compose/topics/create_topic.html', {"form": CreateTopic(request.POST)}, messages)

    if room_slug:

        room = Topic.objects.get(slug=room_slug)
        form = CreateTopic(instance=room)

        return render(request, 'posts/compose/topics/create_topic.html', {"form": form})

    return redirect('open_form')

@auth_required
def delete_room(request, room_slug):

    room = Topic.objects.get(slug=room_slug)
    room.delete()

    return redirect('show_list_of_rooms')