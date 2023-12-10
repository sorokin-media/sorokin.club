# django imports
from django.forms import ModelForm, TextInput, Textarea, ModelChoiceField, Select, ValidationError, CharField

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

    def __init__(self, *args, **kwargs):
        
        self.cool_intro_id = kwargs.pop('cool_intro_id', None)
        super().__init__(*args, **kwargs)
        self.order_field_value = self.data.get('order')

    class Meta:
        model = CoolIntro

        fields = (
            'name',
            'text',
            'image_url',
            'order',
            'telegram_id',
            'test_user'
        )

        widgets = {
            'name': TextInput(attrs={'placeholder': 'Название сообщения'}),
            'text': Textarea(
                attrs={'placeholder': 'Сюды тексты сообщения набери'})
        }

    def clean_order(self):
        ''' валидация для поля order, которая позволит заменять порядок '''

        cleaned_data = super().clean()
        order = cleaned_data.get('order')
        telegram_id = cleaned_data.get('telegram_id')

        if order and \
            CoolIntro.objects.filter(id=self.cool_intro_id).exists() and \
                CoolIntro.objects.filter(order=order).exists() and \
                CoolIntro.objects.filter(order=order).first().order == order:

            if self.cool_intro_id:
                return self.instance.order

            else:
                raise ValidationError("Такой порядок отправки уже занят. "
                                    "Если хочешь сделать замену, сначала сделай "
                                    "форму с тем номером порядка, на который хочешь "
                                    "заменить. ")

        return order

    def clean_telegram_id(self):
        ''' валидация поля telegram_id '''
        telegram_id = self.data.get('telegram_id')

        if not User.objects.filter(telegram_id=telegram_id).exists():
            raise ValidationError("Пользователя с таким telegram_id "
                                  "нет в нашей базе данных")

        return telegram_id


    def save(self, commit=True):
        ''' метод сохранения данных из формы  '''

        cleaned_data = super().clean()
        order = cleaned_data.get('order')

        instance = super().save(commit=False)
 
        if self.order_field_value and self.cool_intro_id and self.order_field_value != instance.order:

            existing_cool_intro = CoolIntro.objects.get(order=self.order_field_value)
            existing_cool_intro.order = instance.order
            # замена на None, чтобы избежать ошибки при сохранении
            instance.order = None
            instance.save()
            existing_cool_intro.save()
            instance.order = self.order_field_value

        instance.save()
        return instance