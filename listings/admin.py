from django.contrib import admin
from .models import Category, Listing, ProfileComment, PrivateMessage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'order')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'condition', 'status', 'owner', 'created_at')
    list_filter = ('category', 'status', 'condition', 'created_at')
    search_fields = ('title', 'description', 'location')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(ProfileComment)
class ProfileCommentAdmin(admin.ModelAdmin):
    list_display = ('profile_user', 'author', 'is_approved_by_ai', 'created_at')
    list_filter = ('is_approved_by_ai',)

@admin.register(PrivateMessage)
class PrivateMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'listing', 'is_blocked_by_ai', 'created_at')
    list_filter = ('is_blocked_by_ai',)