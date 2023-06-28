# django imports
from django.forms import ModelForm, TextInput, Textarea, ModelChoiceField, Select

# import models
from bot.models.cool_intros import CoolIntro
from users.models.user import User

class CoolIntroForm(ModelForm):

    test_user = ModelChoiceField(
        label='Пользователь',
        queryset=User.objects.filter(roles='{god}'),
        empty_label=None,
        widget=Select(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = CoolIntro

        fields = ('name', 'text', 'image_url', 'order', 'test_user')

        widgets = {
            'name': TextInput(attrs={'placeholder': 'Название сообщения'}),
            'text': Textarea(
                attrs={'placeholder': 'Сюды тексты сообщения набери'})
        }
