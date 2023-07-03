# import Django packages
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse

# import Forms and Models
from users.models.user import User
from auth.models import Session

# import config data
from club.settings import TG_ALEX, TG_DEVELOPER_DMITRY, TG_NUTA

# import class for sending message in Telegram
from bot.sending_message import TelegramCustomMessage, MessageToDmitry

# auth imports
from auth.helpers import auth_required, set_session_cookie
from auth.views.auth import logout

#def user_interface(request):
#    return HttpResponse('ok')

@auth_required
def user_interface(request):
    if request.method == 'POST':
        slug = request.POST['slug']
        if User.objects.filter(slug=slug).exists():
            logout(request)
            user = User.objects.filter(slug=slug).first()
            session = Session.create_for_user(user)
            redirect_to = reverse("profile", args=[user.slug])
            response = redirect(redirect_to)
            return set_session_cookie(response, user, session)
        return HttpResponse('ok')
    return render(request, 'auth/user_interface.html')
