from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone = models.CharField(max_length=15, blank=True, verbose_name='Телефон')
    vk_profile = models.CharField(
        max_length=30,
        blank=True,
        default='',
        db_index=True,
        verbose_name='Профиль Вконтакте'
    )
    fb_profile = models.CharField(
        max_length=30,
        blank=True,
        default='',
        db_index=True,
        verbose_name='Профиль Facebook'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.get_full_name()


class Session(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь')
    access_token = models.CharField(max_length=32, db_index=True)
    refresh_token = models.CharField(max_length=32)
    time = models.FloatField()

    class Meta:
        verbose_name = 'Сессия'
        verbose_name_plural = 'Сессии'

    def __str__(self):
        return 'user - %s' % self.user.username


class Band(models.Model):
    leader = models.ForeignKey(User, verbose_name='Лидер группы', null=True, blank=True)
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=200, blank=True, default='')

    class Meta:
        verbose_name = 'Музыкальная группа'
        verbose_name_plural = 'Музыкальные группы'

    def __str__(self):
        return 'Name: %s; Description: %s;' % (self.name, self.description)


class Instrument(models.Model):
    name = models.CharField(max_length=25, verbose_name='Название')

    class Meta:
        verbose_name = 'Музыкальный инструмент'
        verbose_name_plural = 'Музыкальные инструменты'

    def __str__(self):
        return self.name


class Member(models.Model):
    user = models.ForeignKey(User)
    band = models.ForeignKey(Band)
    instrument = models.ForeignKey(Instrument)

    class Meta:
        verbose_name = 'Участник музыкальной группы'
        verbose_name_plural = 'Участники музыкальных групп'

    def __str__(self):
        return '%s; Band: %s; Instrument: %s' % (
            self.user.username,
            self.band.name,
            self.instrument.name
        )
