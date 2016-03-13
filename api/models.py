from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from guardian.shortcuts import assign_perm


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
        full_name = self.get_full_name()
        if full_name:
            return "full_name: %s (id: %d)" % (full_name, self.id)
        else:
            return "username: %s (id: %d)" % (self.username, self.id)

    def save(self, *args, **kwargs):
        is_new = True
        if self.pk:
            is_new = False
        super(User, self).save(*args, **kwargs)
        if is_new:
            Group.objects.get(name=settings.DEFAULT_USER_GROUP).user_set.add(self)
            assign_perm('api.change_user', self, self)


def get_anonymous_user_instance(User):
    return User(id=-1, username='Anonymous')


class Session(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', related_name='sessions')
    access_token = models.CharField(max_length=32, unique=True)
    refresh_token = models.CharField(max_length=32)
    time = models.FloatField(verbose_name='Время создания сессии')

    class Meta:
        verbose_name = 'Сессия'
        verbose_name_plural = 'Сессии'

    def __str__(self):
        return 'user - %s' % self.user.username


class Band(models.Model):
    leader = models.ForeignKey(User, verbose_name='Лидер группы', null=True, blank=True)
    name = models.CharField(max_length=50, verbose_name='Название')
    description = models.TextField(max_length=200, blank=True, default='', verbose_name='Описание')

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


# def upload_to():
#
#
#
# class Sound(models.Model):
#     name = models.CharField()
#     instrument = models.ForeignKey(Instrument, related_name='sounds')
#     file = models.FileField(upload_to=upload_to)


class Member(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь')
    band = models.ForeignKey(Band, related_name='members', verbose_name='Группа')
    instrument = models.ForeignKey(Instrument, related_name='members', verbose_name='Инструмент')

    class Meta:
        verbose_name = 'Участник музыкальной группы'
        verbose_name_plural = 'Участники музыкальных групп'

    def __str__(self):
        return '%s; Band: %s; Instrument: %s' % (
            self.user.username,
            self.band.name,
            self.instrument.name
        )


class Composition(models.Model):
    band = models.ForeignKey(Band, related_name='compositions', verbose_name='Группа')
    name = models.CharField(max_length=30, verbose_name='Название')

    class Meta:
        verbose_name = 'Композиция'
        verbose_name_plural = 'Композиции'

    def __str__(self):
        return 'Composition %s' % self.name


class Track(models.Model):
    instrument = models.ForeignKey(Instrument, related_name='tracks', verbose_name='Инструмент')
    track = models.TextField(verbose_name='Дорожка')
    composition = models.ForeignKey(Composition, related_name='tracks', verbose_name='Композиция')

    class Meta:
        verbose_name = 'Дорожка'
        verbose_name_plural = 'Дорожки'
