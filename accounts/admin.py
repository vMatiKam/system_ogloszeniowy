from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'city', 'show_phone')
    search_fields = ('user__username', 'user__email', 'city', 'phone_number')