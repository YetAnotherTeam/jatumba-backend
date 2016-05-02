from django.conf import settings
from django.db import models

from api.models.organization import Band


class Message(models.Model):
    band = models.ForeignKey(
        Band,
        on_delete=models.CASCADE,
        verbose_name='Музыкальная группа'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    datetime = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=500, verbose_name='Текст')

    class Meta:
        index_together = (('band', 'datetime'),)
        ordering = ('-datetime',)
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
