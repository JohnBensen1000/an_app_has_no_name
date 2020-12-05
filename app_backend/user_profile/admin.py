from django.contrib import admin

# Register your models here.
from .models import UserProfile, Relationships

admin.site.register(UserProfile)
admin.site.register(Relationships)