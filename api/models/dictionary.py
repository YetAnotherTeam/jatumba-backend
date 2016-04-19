import os

from audiofield.fields import AudioField
from django.conf import settings
from django.db import models

from utils.django.storage import OverwriteStorage


class Instrument(models.Model):
    name = models.CharField(max_length=25, verbose_name='Название', unique=True)

    class Meta:
        verbose_name = 'Музыкальный инструмент'
        verbose_name_plural = 'Музыкальные инструменты'

    def __str__(self):
        return self.name


def sounds_path(instance, filename):
    return os.path.join(
        'instrument',
        instance.instrument.name,
        "%s.%s" % (instance.name, filename.split('.')[-1])
    )


class Sound(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    instrument = models.ForeignKey(
        Instrument,
        on_delete=models.CASCADE,
        related_name='sounds',
        verbose_name='Инструмент'
    )
    file = AudioField(
        upload_to=sounds_path,
        ext_whitelist=(".mp3", ".wav", ".ogg"),
        storage=OverwriteStorage(),
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
