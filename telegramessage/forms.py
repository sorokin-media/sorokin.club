from django.forms import ModelForm, TextInput, Textarea
from telegramessage.models import TelegramMesage, DayHelpfulness

class CreateMessage(ModelForm):

    class Meta:
        model = TelegramMesage

        fields = ('name', 'text', 'image_url', 'is_finish_of_queue', 'days', 'hours', 'minutes')

        widgets = {
            'name': TextInput(attrs={'placeholder': 'Название сообщения'}),
            'text': Textarea(
                attrs={'placeholder': 'Сюды тексты сообщения набери'})
        }


class CreateDayHelpfullness(ModelForm):

    class Meta:
        model = DayHelpfulness

        fields = ('name', 'text', 'image_url', 'order')

        widgets = {
            'name': TextInput(attrs={'placeholder': 'Название сообщения'}),
            'text': Textarea(
                attrs={'placeholder': 'Сюды тексты сообщения набери'})
        }
