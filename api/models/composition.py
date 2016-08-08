from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.transaction import atomic
from django.utils import timezone
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

    @atomic
    def assign_perms(self):
        for perm in ('api.change_composition', 'api.delete_composition'):
            assign_perm(perm, self.band.group, self)


class AbstractTrack(models.Model):
    SECTOR_LENGTH = 32
    entity = JSONField(verbose_name='Сущность')
    order = models.PositiveSmallIntegerField(verbose_name='Порядок')

    class Meta:
        abstract = True
        verbose_name = 'Абстрактная дорожка'
        verbose_name_plural = 'Абстрактные дорожки'


class Track(AbstractTrack):
    instrument = models.ForeignKey(
        Instrument,
        on_delete=models.CASCADE,
        related_name='tracks',
        verbose_name='Инструмент'
    )
    composition_version = models.ForeignKey(
        'CompositionVersion',
        on_delete=models.CASCADE,
        related_name='tracks',
        verbose_name='Версия композиции'
    )

    class Meta:
        unique_together = (('composition_version', 'order'),)
        ordering = ('composition_version', 'order')
        verbose_name = 'Дорожка'
        verbose_name_plural = 'Дорожки'

    def __str__(self):
        return (
            '№{order} | {composition_version}'
            .format(order=self.order, composition_version=self.composition_version)
        )


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
    create_datetime = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('-create_datetime',)
        index_together = ('composition', 'id')
        verbose_name = 'Версия композиции'
        verbose_name_plural = 'Версии композиций'

    def __str__(self):
        return str(self.composition)

    @classmethod
    @atomic
    def copy_from_diff_version(cls, last_diff_version, user_id):
        version = cls.objects.create(
            composition_id=last_diff_version.composition_id,
            author_id=user_id
        )
        for diff_track in last_diff_version.tracks.all():
            Track.objects.create(
                composition_version=version,
                instrument=diff_track.instrument,
                entity=diff_track.entity,
                order=diff_track.order
            )
        return version

    @atomic
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(CompositionVersion, self).save(force_insert, force_update, using, update_fields)
        (
            LastCompositionVersionLink.objects
            .using(using)
            .update_or_create(
                defaults={'composition_version_id': self.id},
                composition=self.composition
            )
        )

    @atomic
    def delete(self, using=None, keep_parents=False):
        super(CompositionVersion, self).delete(using, keep_parents)
        composition_version = (
            CompositionVersion.objects
            .filter(composition=self.composition)
            .using(using)
            .last()
        )
        if composition_version:
            (
                LastCompositionVersionLink.objects
                .using(using)
                .update_or_create(
                    defaults={'composition_version_id': composition_version.id},
                    composition=self.composition
                )
            )


class LastCompositionVersionLink(models.Model):
    composition = models.OneToOneField(
        Composition,
        on_delete=models.CASCADE,
        related_name='last_composition_version_link',
        verbose_name='Композиция'
    )
    composition_version = models.OneToOneField(
        CompositionVersion,
        on_delete=models.CASCADE,
        related_name='last_composition_version_link',
        verbose_name='Версия композиции'
    )

    class Meta:
        verbose_name = 'Связь между последней версией композиции и композицией'
        verbose_name_plural = 'Связи между последними версиями композиций и композициями'


class DiffTrack(AbstractTrack):
    instrument = models.ForeignKey(
        Instrument,
        on_delete=models.CASCADE,
        related_name='diff_tracks',
        verbose_name='Инструмент'
    )
    diff_composition_version = models.ForeignKey(
        'DiffCompositionVersion',
        on_delete=models.CASCADE,
        related_name='tracks',
        verbose_name='Версия композиции'
    )

    class Meta:
        unique_together = (('diff_composition_version', 'order'),)
        ordering = ('diff_composition_version', 'order')
        verbose_name = 'Дифф-дорожка'
        verbose_name_plural = 'Дифф-дорожки'

    def __str__(self):
        return (
            '№{order} | {diff_composition_version}'
            .format(order=self.order, diff_composition_version=self.diff_composition_version)
        )


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

    @classmethod
    @atomic
    def copy_from_version(cls, last_composition_version):
        diff_version = cls.objects.create(composition_id=last_composition_version.composition_id)
        for track in last_composition_version.tracks.all():
            DiffTrack.objects.create(
                diff_composition_version=diff_version,
                instrument=track.instrument,
                entity=track.entity,
                order=track.order
            )
        return diff_version


class Fork(models.Model):
    source_composition = models.ForeignKey(
        Composition,
        on_delete=models.CASCADE,
        related_name='as_source_forks',
        verbose_name='Композиция, которую форкнули'
    )
    source_composition_version = models.ForeignKey(
        CompositionVersion,
        on_delete=models.CASCADE,
        related_name='forks',
        verbose_name='Версия композиции'
    )
    destination_composition = models.OneToOneField(
        Composition,
        on_delete=models.CASCADE,
        related_name='as_destination_fork',
        verbose_name='Новая композиция'
    )

    class Meta:
        verbose_name = 'Форк'
        verbose_name_plural = 'Форки'
