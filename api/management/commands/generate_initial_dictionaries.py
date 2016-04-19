import os

from django.core.files import File
from django.core.management.base import BaseCommand

from api.models import Instrument, Sound


class Command(BaseCommand):
    DATA_DIR = 'dictionaries_data'
    help = 'Заполняет таблицы инструментов, звуков, жанров начальными данными'

    def handle(self, *args, **options):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        dictionaries_path = os.path.join(base_dir, self.DATA_DIR)
        instruments_dirs = os.listdir(dictionaries_path)
        for instrument_dir in instruments_dirs:
            # Игнорируем скрытые папки и файлы.
            if not instrument_dir.startswith('.'):
                instrument, _ = Instrument.objects.get_or_create(name=instrument_dir)
                sounds_path = os.path.join(dictionaries_path, instrument_dir)
                sounds_names = [
                    sound_name for sound_name in os.listdir(sounds_path)
                    if os.path.isfile(os.path.join(sounds_path, sound_name)) and
                    not sound_name.startswith('.')
                    ]
                for sound_name in sounds_names:
                    with open(os.path.join(sounds_path, sound_name), 'rb') as sound_file:
                        wrapped_file = File(sound_file)
                        sound, _ = Sound.objects.get_or_create(
                            name=os.path.splitext(sound_name)[0],
                            instrument=instrument
                        )
                        sound.file = wrapped_file
                        sound.save()
        self.stdout.write(self.style.SUCCESS('Successfully created'))
