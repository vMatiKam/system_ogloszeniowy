from django.contrib import admin
from .models import Category, Listing, ListingComment, PrivateMessage

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

@admin.register(ListingComment)
class ListingCommentAdmin(admin.ModelAdmin):
    list_display = ('listing', 'author', 'is_approved_by_ai', 'created_at')
    list_filter = ('is_approved_by_ai', 'created_at')
    search_fields = ('content', 'listing__title', 'author__username')

@admin.register(PrivateMessage)
class PrivateMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'listing', 'is_blocked_by_ai', 'created_at')
    list_filter = ('is_blocked_by_ai',)