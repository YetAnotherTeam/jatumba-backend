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


class CompositionVersion(models.Model):
    composition = models.ForeignKey(
        Composition,
        on_delete=models.PROTECT,
        related_name='versions',
        verbose_name='Композиция'
    )

    class Meta:
        index_together = ('composition', 'id')
        verbose_name = 'Версия композиции'
        verbose_name_plural = 'Версии композиций'

    # def __str__(self):
    #     return self


class Track(models.Model):
    instrument = models.ForeignKey(
        Instrument,
        on_delete=models.CASCADE,
        related_name='tracks',
        verbose_name='Инструмент'
    )
    entity = JSONField(verbose_name='Сущность', null=True)
    composition_version = models.ForeignKey(
        CompositionVersion,
        on_delete=models.CASCADE,
        related_name='tracks',
        verbose_name='Композиция'
    )

    class Meta:
        verbose_name = 'Дорожка'
        verbose_name_plural = 'Дорожки'

    def __str__(self):
        return str(self.composition)
