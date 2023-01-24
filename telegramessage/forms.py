from django.forms import ModelForm, CharField, TextInput, Textarea, IntegerField, Form, BooleanField
from .models import TelegramMesage
from datetime import date


class CreateMessage(ModelForm):
    class Meta:
        model = TelegramMesage
        fields = ('name', 'text', 'image_url', 'is_finish_of_queue', 'is_archived', 'days', 'hours', 'minutes')

        widgets = {
            'name': TextInput(attrs={'placeholder': 'Название сообщения'}),
            'text': Textarea(
                attrs={'placeholder': 'Сюды тексты сообщения набери'})
        }        