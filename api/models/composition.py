from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.transaction import atomic

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

    @atomic
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        is_new = not self.pk
        super(Composition, self).save(force_insert, force_update, using, update_fields)
        if is_new:
            CompositionVersion.objects.create(composition=self)


class CompositionVersion(models.Model):
    composition = models.ForeignKey(
        Composition,
        on_delete=models.CASCADE,
        related_name='versions',
        verbose_name='Композиция'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='composition_versions',
        verbose_name='Автор'
    )
    create_datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = ('composition', 'id')
        verbose_name = 'Версия композиции'
        verbose_name_plural = 'Версии композиций'

    def __str__(self):
        return str(self.composition)


class AbstractTrack(models.Model):
    SECTOR_LENGTH = 32
    entity = JSONField(verbose_name='Сущность', null=True)
    order = models.PositiveSmallIntegerField(verbose_name='Порядок')

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.composition)


class Track(AbstractTrack):
    instrument = models.ForeignKey(
        Instrument,
        on_delete=models.CASCADE,
        related_name='tracks',
        verbose_name='Инструмент'
    )
    composition_version = models.ForeignKey(
        CompositionVersion,
        on_delete=models.CASCADE,
        related_name='tracks',
        verbose_name='Версия композиции'
    )

    class Meta:
        unique_together = (('composition_version', 'order'),)
        ordering = ('composition_version', 'order')
        verbose_name = 'Дорожка'
        verbose_name_plural = 'Дорожки'


class DiffCompositionVersion(models.Model):
    composition = models.ForeignKey(
        Composition,
        on_delete=models.CASCADE,
        related_name='diff_versions',
        verbose_name='Композиция'
    )

    class Meta:
        index_together = ('composition', 'id')
        verbose_name = 'Дифф-версия композиции'
        verbose_name_plural = 'Дифф-версии композиций'

    def __str__(self):
        return str(self.composition)


class DiffTrack(AbstractTrack):
    instrument = models.ForeignKey(
        Instrument,
        on_delete=models.CASCADE,
        related_name='diff_tracks',
        verbose_name='Инструмент'
    )
    diff_composition_version = models.ForeignKey(
        DiffCompositionVersion,
        on_delete=models.CASCADE,
        related_name='diff_tracks',
        verbose_name='Версия композиции'
    )

    class Meta:
        unique_together = (('diff_composition_version', 'order'),)
        ordering = ('diff_composition_version', 'order')
        verbose_name = 'Дифф-дорожка'
        verbose_name_plural = 'Дифф-дорожки'


class Fork(models.Model):
    composition_version = models.ForeignKey(
        CompositionVersion,
        on_delete=models.CASCADE,
        related_name='forks',
        verbose_name='Версия композиции'
    )
    composition = models.OneToOneField(
        Composition,
        on_delete=models.CASCADE,
        related_name='fork',
        verbose_name='Композиция'
    )

    class Meta:
        verbose_name = 'Форк'
        verbose_name_plural = 'Форки'
