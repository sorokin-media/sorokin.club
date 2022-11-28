# Generated by Django 3.2.13 on 2022-11-28 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0028_auto_20221127_0510'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalpost',
            name='type',
            field=models.CharField(choices=[('post', 'Текст'), ('intro', '#intro'), ('link', 'Ссылка'), ('question', 'Вопрос'), ('idea', 'Идея'), ('project', 'Проект'), ('event', 'Событие'), ('referral', 'Рефералка'), ('battle', 'Батл'), ('weekly_digest', 'Журнал Клуба'), ('guide', 'Путеводитель'), ('thread', 'Тред')], db_index=True, default='post', max_length=32),
        ),
        migrations.AlterField(
            model_name='post',
            name='type',
            field=models.CharField(choices=[('post', 'Текст'), ('intro', '#intro'), ('link', 'Ссылка'), ('question', 'Вопрос'), ('idea', 'Идея'), ('project', 'Проект'), ('event', 'Событие'), ('referral', 'Рефералка'), ('battle', 'Батл'), ('weekly_digest', 'Журнал Клуба'), ('guide', 'Путеводитель'), ('thread', 'Тред')], db_index=True, default='post', max_length=32),
        ),
    ]
