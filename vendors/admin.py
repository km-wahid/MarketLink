from django.contrib import admin
from .models import VendorProfile

@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'user_email', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['business_name', 'user__email']
    readonly_fields = ['created_at']

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "User Email"
