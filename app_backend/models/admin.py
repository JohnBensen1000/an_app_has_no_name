from django.contrib import admin

from .models import *
# Register your models here.
admin.site.register(Preferences)
admin.site.register(Profile)
admin.site.register(User)
admin.site.register(Relationships)
admin.site.register(Chat)
admin.site.register(ChatMember)
admin.site.register(Post)