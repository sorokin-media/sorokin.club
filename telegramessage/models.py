from datetime import datetime, timedelta
from uuid import uuid4
import pytz

from django.db import models

from users.models.user import User


class TelegramMesage(models.Model):
    '''Messages that are sent according to the schedule from the moment of registration. '''
    class Meta:
        db_table = 'telegram_messages'

    TRUE_FALSE_CHOICES = (
        (True, 'Yes'),
        (False, 'No')
    )

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(unique=True, null=False, blank=False, max_length=256, verbose_name='Название сообщения')
    text = models.TextField(null=True, blank=True, verbose_name='Текст сообщения')
    image_url = models.CharField(null=True, blank=True, max_length=256, verbose_name='Ссылка на изображение')
    is_finish_of_queue = models.BooleanField(null=False,
                                             choices=TRUE_FALSE_CHOICES,
                                             verbose_name='Сообщение является'
                                                          ' конечным в серии '
                                                          'сообщений',
                                             default=False)
    is_archived = models.BooleanField(null=False,
                                      choices=TRUE_FALSE_CHOICES,
                                      verbose_name='Сохранить как черновик',
                                      default=False)
    days = models.PositiveIntegerField(null=False, blank=False, verbose_name='Дни задержки', default=0)
    hours = models.PositiveBigIntegerField(null=False, blank=False, verbose_name='Часы задержки', default=0)
    minutes = models.PositiveBigIntegerField(null=False, blank=False, verbose_name='Минуты задержки', default=0)
    test_user = models.ForeignKey(User, related_name='test_user', on_delete=models.CASCADE, null=True)

    def set_time_of_delay(self, days, hours, minutes):
        time_zone = pytz.UTC
        now = time_zone.localize(datetime.utcnow())
        time_delay = now + timedelta(days=days,
                                     hours=hours,
                                     minutes=minutes)
        return time_delay

    def save_data(self, name, text, image_url, is_finish_of_queue, is_archived, test_user,
                  days=0, hours=0, minutes=0):
        self.name = name
        self.text = text
        self.image_url = image_url
        self.is_finish_of_queue = is_finish_of_queue
        self.is_archived = is_archived
#        self.time_delay = self.set_time_of_delay(days, hours, minutes)
        self.days = days
        self.hours = hours
        self.minutes = minutes
        self.test_user=test_user
        self.save()

    def update_data(self, name, text, image_url, is_finish_of_queue, is_archived,
                    days=0, hours=0, minutes=0):
        self.name = name
        self.text = text
        self.image_url = image_url
        self.is_finish_of_queue = is_finish_of_queue
        self.is_archived = is_archived
        self.time_delay = self.set_time_of_delay(days, hours, minutes)

    def return_data_for_html(self):
        name = self.name
        text = self.text
        image_url = self.image_url
        is_finish_of_queue = self.is_finish_of_queue
        is_archived = self.is_archived
        return ([name, text, image_url, is_finish_of_queue, is_archived])


class TelegramMesageQueue(models.Model):
    '''Queue Model for objects of Model TelegramMesage '''
    class Meta:
        db_table = 'telegram_messages_queue'

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user_to = models.ForeignKey(User, related_name='message_queue', on_delete=models.CASCADE)
    last_message = models.ForeignKey(TelegramMesage, related_name='last_message_id',
                                     on_delete=models.CASCADE, null=True)
    first_time_was_sended = models.DateTimeField(blank=True, null=True)
    is_series_finished = models.BooleanField(default=False)
    last_time_message_sended = models.DateTimeField(blank=True, null=True)
    id_of_sended_messages = models.TextField(blank=True, null=True)

    # be careful: time

    def save_time_message_sended(self):
        time_zone = pytz.UTC
        now = time_zone.localize(datetime.utcnow())
        self.last_time_message_sended = now
        self.save()

    def get_string_of_ids(self):
        # if that would not be first id in queue
        return str(self.id_of_sended_messages) if self.id_of_sended_messages is not None else None

    def push_new_id(self, id_of_message):
        string_of_ids = self.get_string_of_ids()
        if string_of_ids is None:
            string_of_ids = ''
        else:
            string_of_ids = string_of_ids + ', '
        string_of_ids = string_of_ids + id_of_message
        self.id_of_sended_messages = string_of_ids
        self.save()

class DayHelpfulness(models.Model):

    class Meta:
        db_table = 'day_help_messages'
        ordering = ['order']
        verbose_name = 'Полезняха дня'

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
    