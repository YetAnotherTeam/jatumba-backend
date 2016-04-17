from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.db.transaction import atomic
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
        return "%s (%d)" % (self.get_full_name(), self.id)

    @atomic
    def save(self, *args, **kwargs):
        is_new = True
        if self.pk:
            is_new = False
        super(User, self).save(*args, **kwargs)
        if is_new:
            group, _ = Group.objects.get_or_create(name=settings.DEFAULT_USER_GROUP)
            group.user_set.add(self)
            assign_perm('api.change_user', self, self)


def get_anonymous_user_instance(User):
    return User(id=-1, username='Anonymous')


class Session(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='sessions'
    )
    access_token = models.CharField(max_length=32, unique=True)
    refresh_token = models.CharField(max_length=32, unique=True)
    time = models.FloatField(verbose_name='Время создания сессии')

    class Meta:
        verbose_name = 'Сессия'
        verbose_name_plural = 'Сессии'

    def __str__(self):
        return self.user
