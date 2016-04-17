from audiofield.admin import AudioFileAdmin
from django.contrib import admin

from api.models import *


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name')
    filter_horizontal = ('groups', 'user_permissions')
    ordering = ['id']


class SoundAdmin(AudioFileAdmin):
    # add 'audio_file_player' tag to your admin view
    list_display = ('name', 'audio_file_player', 'instrument')
    actions = ['custom_delete_selected']
    ordering = ['instrument', 'name']

    def custom_delete_selected(self, request, queryset):
        # custom delete code
        count = queryset.count()
        for sound in queryset:
            if sound.file:
                if os.path.exists(sound.file.path):
                    os.remove(sound.file.path)
            sound.delete()
        self.message_user(request, "Successfully deleted %d audio files." % count)

    custom_delete_selected.short_description = "Delete selected items"

    def get_actions(self, request):
        actions = super(AudioFileAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions


admin.site.register(User, UserAdmin)
admin.site.register(Session)
admin.site.register(Band)
admin.site.register(Genre)
admin.site.register(Sound, SoundAdmin)
admin.site.register(Instrument)
admin.site.register(Member)
admin.site.register(Composition)
admin.site.register(Track)
