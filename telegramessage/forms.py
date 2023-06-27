# django imports
from django.forms import ModelForm, TextInput, Textarea, ModelChoiceField, Select

# import models
from telegramessage.models import TelegramMesage, DayHelpfulness
from users.models.user import User


class CreateMessage(ModelForm):

    test_user = ModelChoiceField(
        label='Пользователь',
        queryset=User.objects.filter(roles='{god}'),
        empty_label=None,
        widget=Select(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = TelegramMesage

        fields = ('name', 'text', 'image_url', 'is_finish_of_queue', 'days', 'hours', 'minutes', 'test_user')

        widgets = {
            'name': TextInput(attrs={'placeholder': 'Название сообщения'}),
            'text': Textarea(
                attrs={'placeholder': 'Сюды тексты сообщения набери'})
        }


class CreateDayHelpfullness(ModelForm):

    test_user = ModelChoiceField(
        label='Пользователь',
        queryset=User.objects.filter(roles='{god}'),
        empty_label=None,
        widget=Select(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = DayHelpfulness

        fields = ('name', 'text', 'image_url', 'order', 'test_user')

        widgets = {
            'name': TextInput(attrs={'placeholder': 'Название сообщения'}),
            'text': Textarea(
                attrs={'placeholder': 'Сюды тексты сообщения набери'})
        }
