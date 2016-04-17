import os
from audiofield.fields import AudioField
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.postgres.fields import JSONField
from django.db import models
from guardian.shortcuts import assign_perm


class Band(Group):
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        verbose_name='Лидер группы'
    )
    description = models.TextField(max_length=200, blank=True, default='', verbose_name='Описание')

    class Meta:
        verbose_name = 'Музыкальная группа'
        verbose_name_plural = 'Музыкальные группы'

    def __str__(self):
        return 'Name: %s; Description: %s;' % (self.name, self.description)

    def save(self, *args, **kwargs):
        is_new = True
        if self.pk:
            is_new = False
        super(Band, self).save(*args, **kwargs)
        if is_new:
            assign_perm('api.change_band', self.leader, self)
            assign_perm('api.delete_band', self.leader, self)


class Instrument(models.Model):
    name = models.CharField(max_length=25, verbose_name='Название', unique=True)

    class Meta:
        verbose_name = 'Музыкальный инструмент'
        verbose_name_plural = 'Музыкальные инструменты'

    def __str__(self):
        return self.name


def instrument_sounds_path(instance, filename):
    return os.path.join(
        'instrument',
        instance.instrument.name,
        "%s.%s" % (instance.name, filename.split('.')[-1])
    )


class Sound(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    instrument = models.ForeignKey(Instrument, related_name='sounds', verbose_name='Инструмент')
    file = AudioField(
        upload_to=instrument_sounds_path,
        ext_whitelist=(".mp3", ".wav", ".ogg"),
        verbose_name='Audio-файл',
        help_text="Allowed type - .mp3, .wav, .ogg"
    )

    def audio_file_player(self):
        """Audio player tag for admin"""
        if self.file:
            file_url = settings.MEDIA_URL + str(self.file)
            player_string = '<ul class="playlist"><li style="width:250px;">\
            <a href="%s">%s</a></li></ul>' % (file_url, os.path.basename(self.file.name))
            return player_string

    audio_file_player.allow_tags = True
    audio_file_player.short_description = 'Audio file player'

    class Meta:
        unique_together = (('instrument', 'name'),)
        verbose_name = 'Звук'
        verbose_name_plural = 'Звуки'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название")

    class Meta:
        verbose_name = 'Музыкальный жанр'
        verbose_name_plural = 'Музыкальные жанры'

    def __str__(self):
        return self.name


class Member(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Пользователь')
    band = models.ForeignKey(Band, related_name='members', verbose_name='Группа')
    instrument = models.ForeignKey(
        Instrument,
        null=True,
        blank=True,
        related_name='members',
        verbose_name='Инструмент'
    )

    class Meta:
        verbose_name = 'Участник музыкальной группы'
        verbose_name_plural = 'Участники музыкальных групп'

    def __str__(self):
        return '%s; Band: %s; Instrument: %s' % (
            self.user.username,
            self.band.name,
            self.instrument.name if self.instrument else ''
        )

    def save(self, *args, **kwargs):
        is_new = True
        if self.pk:
            is_new = False
        super(Member, self).save(*args, **kwargs)
        if is_new:
            assign_perm('api.delete_member', self.user, self)
            assign_perm('api.delete_member', self.band.leader, self)
            self.user.groups.add(self.band)


class Composition(models.Model):
    band = models.ForeignKey(Band, related_name='compositions', verbose_name='Группа')
    name = models.CharField(max_length=30, verbose_name='Название')
    genres = models.ManyToManyField(
        Genre,
        blank=True,
        related_name='compositions',
        verbose_name='Жанры'
    )

    class Meta:
        verbose_name = 'Композиция'
        verbose_name_plural = 'Композиции'

    def __str__(self):
        return self.name


class Track(models.Model):
    instrument = models.ForeignKey(Instrument, related_name='tracks', verbose_name='Инструмент')
    track = JSONField(verbose_name='Дорожка')
    composition = models.ForeignKey(Composition, related_name='tracks', verbose_name='Композиция')

    # version = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Дорожка'
        verbose_name_plural = 'Дорожки'

    def save(self, *args, **kwargs):
        is_new = True
        if self.pk:
            is_new = False
        super(Track, self).save(*args, **kwargs)
        if is_new:
            assign_perm('api.change_track', self.composition.band, self)
            assign_perm('api.delete_track', self.composition.band, self)


class TrackHistory(models.Model):
    track = JSONField(verbose_name='Дорожка')
    track_key = models.ForeignKey(
        Track,
        related_name='track_history',
        verbose_name='Текущая версия дорожки'
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='tracks_modified',
        verbose_name='Автор изменения'
    )

    class Meta:
        verbose_name = 'Старая версия дорожки'
        verbose_name_plural = 'Старые версии дорожки'
