from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.db.transaction import atomic
from guardian.shortcuts import assign_perm, remove_perm


class Band(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Авторизационная группа'
    )
    lead_members = models.ManyToManyField(
        'Member',
        through='Leader',
        related_name='as_leader_bands',
        verbose_name='Лидер'
    )
    description = models.TextField(max_length=200, blank=True, default='', verbose_name='Описание')

    class Meta:
        verbose_name = 'Музыкальная группа'
        verbose_name_plural = 'Музыкальные группы'

    def __str__(self):
        return self.name

    @atomic
    def save(self, *args, **kwargs):
        is_new = not self.pk
        super(Band, self).save(*args, **kwargs)

        if is_new:
            group, _ = Group.objects.get_or_create(name='band.%d' % self.id)
            self.group = group
            self.save(update_fields=('group',))


class Member(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name='Пользователь'
    )
    band = models.ForeignKey(
        Band,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name='Группа'
    )

    class Meta:
        unique_together = (('user', 'band'),)
        verbose_name = 'Участник музыкальной группы'
        verbose_name_plural = 'Участники музыкальных групп'

    def __str__(self):
        return '%s (%s)' % (str(self.user), self.band.name)

    @atomic
    def save(self, *args, **kwargs):
        is_new = not self.id

        super(Member, self).save(*args, **kwargs)

        if is_new:
            assign_perm('api.change_member', self.user, self)
            assign_perm('api.delete_member', self.user, self)

            self.user.groups.add(self.band.group)

    @atomic
    def delete(self, using=None, keep_parents=False):
        self.user.groups.remove(self.band.group)
        super(Member, self).delete(using, keep_parents)


class Leader(models.Model):
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='leader',
        verbose_name='Участник музыкальной группы'
    )
    band = models.OneToOneField(
        Band,
        on_delete=models.CASCADE,
        related_name='leader',
        verbose_name='Музыкальная группа'
    )

    class Meta:
        verbose_name = 'Лидер музыкальной группы'
        verbose_name_plural = 'Лидеры музыкальных групп'

    def __str__(self):
        return str(self.member)

    @atomic
    def save(self, *args, **kwargs):
        is_new = not self.id

        super(Leader, self).save(*args, **kwargs)

        if is_new:
            user = self.member.user
            assign_perm('api.change_band', user, self.band)
            assign_perm('api.delete_band', user, self.band)

    @atomic
    def delete(self, using=None, keep_parents=False):
        user = self.member.user
        remove_perm('api.change_band', user, self.band)
        remove_perm('api.delete_band', user, self.band)

        user.groups.remove(self.band.group)
        super(Leader, self).delete(using, keep_parents)
