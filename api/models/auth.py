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