from datetime import datetime, timedelta
from uuid import uuid4
import pytz

from django.db import models

from users.models.user import User


class CoolIntro(models.Model):
    ''' Model is similar with model DayHelpfulness '''
    class Meta:
        db_table = 'cool_intros'
        app_label = 'bot'
    
    TRUE_FALSE_CHOICES = (
        (True, 'Yes'),
        (False, 'No')
    )

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(unique=True, null=False, blank=False, max_length=256, verbose_name='Название сообщения')
    text = models.TextField(null=True, blank=True, verbose_name='Текст сообщения')
    image_url = models.CharField(default=None, blank=True, max_length=256, verbose_name='Ссылка на изображение')
    order = models.IntegerField(null=True, unique=True, verbose_name='Порядок отправки')
    is_archived = models.BooleanField(null=False,
                                      choices=TRUE_FALSE_CHOICES,
                                      verbose_name='Сохранить как черновик',
                                      default=False)
    is_sended = models.BooleanField(null=False, default=False)
    test_user = models.ForeignKey(User, related_name='cool_intros_test_users', on_delete=models.CASCADE, null=True)
