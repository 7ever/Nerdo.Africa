from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'is_verified', 'ajira_id')
    list_editable = ('is_verified',) # Allows toggling checkbox in the list view
    list_filter = ('is_verified', 'is_phone_verified')
    search_fields = ('user__username', 'phone_number', 'ajira_id')