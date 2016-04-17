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


class CompositionBranch(models.Model):
    name = models.CharField(max_length=50)
    composition = models.ForeignKey(
        Composition,
        on_delete=models.CASCADE,
        related_name='branches',
        verbose_name='Композиция'
    )

    class Meta:
        verbose_name = 'Ветка'
        verbose_name_plural = 'Ветки'

    def __str__(self):
        return self.name


class Track(models.Model):
    instrument = models.ForeignKey(
        Instrument,
        on_delete=models.CASCADE,
        related_name='tracks',
        verbose_name='Инструмент'
    )
    composition = models.ForeignKey(
        Composition,
        on_delete=models.CASCADE,
        related_name='tracks',
        verbose_name='Композиция'
    )

    class Meta:
        verbose_name = 'Дорожка'
        verbose_name_plural = 'Дорожки'

    def __str__(self):
        return str(self.composition)

    @atomic
    def save(self, *args, **kwargs):
        is_new = not self.pk
        super(Track, self).save(*args, **kwargs)
        if is_new:
            assign_perm('api.change_track', self.composition.band.group, self)
            assign_perm('api.delete_track', self.composition.band.group, self)


class AbstractTrackSnapshot(models.Model):
    entity = JSONField(verbose_name='Дорожка')

    class Meta:
        abstract = True
        verbose_name = 'Снимок дорожки'
        verbose_name_plural = 'Снимки дорожки'


class TrackSnapshot(AbstractTrackSnapshot):
    track = models.ForeignKey(
        Track,
        on_delete=models.CASCADE,
        related_name='snapshots',
        verbose_name='Дорожка'
    )
    branch = models.ForeignKey(
        CompositionBranch,
        on_delete=models.CASCADE,
        related_name='snapshots',
        verbose_name='Ветка'
    )

    class Meta:
        verbose_name = 'Снимок дорожки'
        verbose_name_plural = 'Снимки дорожки'


class AbstractTrackDiff(models.Model):
    entity = JSONField(verbose_name='Сущность')

    class Meta:
        abstract = True
        verbose_name = 'Изменение дорожки'
        verbose_name_plural = 'Изменения дорожек'


class TrackDiff(AbstractTrackDiff):
    snapshot = models.ForeignKey(
        TrackSnapshot,
        on_delete=models.CASCADE,
        related_name='diffs',
        verbose_name='Снимок'
    )
    track = models.ForeignKey(
        Track,
        on_delete=models.CASCADE,
        related_name='diffs',
        verbose_name='Дорожка'
    )
    branch = models.ForeignKey(
        CompositionBranch,
        on_delete=models.CASCADE,
        related_name='diffs',
        verbose_name='Ветка'
    )

    class Meta:
        verbose_name = 'Изменение дорожки'
        verbose_name_plural = 'Изменения дорожек'


# Цепочечная последовательная схема без разветвлений, за зафиксированным снапшотом идет дифф,
# потом создается Коллаборативный-снапшот, дифф - ребро графа, снапшот - конечная вершина
class CollaborateTrackDiff(AbstractTrackDiff):
    snapshot = models.ForeignKey(
        TrackSnapshot,
        on_delete=models.CASCADE,
        related_name='collaborate_diffs',
        verbose_name='Снимок'
    )

    class Meta:
        verbose_name = 'Коллаборативное изменение дорожки'
        verbose_name_plural = 'Коллаборативные изменения дорожек'


class CollaborateTrackSnapshot(AbstractTrackSnapshot):
    diff = models.OneToOneField(CollaborateTrackDiff)
    track = models.ForeignKey(
        Track,
        on_delete=models.CASCADE,
        related_name='collaborate_snapshots',
        verbose_name='Коллаборативная дорожка'
    )
    branch = models.ForeignKey(
        CompositionBranch,
        on_delete=models.CASCADE,
        related_name='collaborate_snapshots',
        verbose_name='Ветка'
    )

    class Meta:
        verbose_name = 'Коллаборативный снимок дорожки'
        verbose_name_plural = 'Коллаборативные снимки дорожек'
