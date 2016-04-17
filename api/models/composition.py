from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.transaction import atomic
from guardian.shortcuts import assign_perm

from api.models.dictionary import Genre, Instrument
from api.models.organization import Band


class Composition(models.Model):
    band = models.ForeignKey(
        Band,
        on_delete=models.CASCADE,
        related_name='compositions',
        verbose_name='Группа'
    )
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
    instrument = models.ForeignKey(
        Instrument,
        on_delete=models.CASCADE,
        related_name='tracks',
        verbose_name='Инструмент'
    )
    track = JSONField(verbose_name='Дорожка')
    composition = models.ForeignKey(
        Composition,
        on_delete=models.CASCADE,
        related_name='tracks',
        verbose_name='Композиция'
    )
    # version = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Дорожка'
        verbose_name_plural = 'Дорожки'

    def __str__(self):
        return str(self.composition)

    @atomic
    def save(self, *args, **kwargs):
        is_new = True
        if self.pk:
            is_new = False
        super(Track, self).save(*args, **kwargs)
        if is_new:
            assign_perm('api.change_track', self.composition.band.group, self)
            assign_perm('api.delete_track', self.composition.band.group, self)


class TrackHistory(models.Model):
    track = JSONField(verbose_name='Дорожка')
    track_key = models.ForeignKey(
        Track,
        on_delete=models.CASCADE,
        related_name='track_history',
        verbose_name='Текущая версия дорожки'
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tracks_modified',
        verbose_name='Автор изменения'
    )

    class Meta:
        verbose_name = 'Старая версия дорожки'
        verbose_name_plural = 'Старые версии дорожки'
