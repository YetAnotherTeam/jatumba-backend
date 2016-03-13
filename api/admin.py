from django.contrib import admin

from .models import *

admin.site.register(User)
admin.site.register(Session)
admin.site.register(Band)
admin.site.register(Member)
admin.site.register(Composition)
admin.site.register(Track)
