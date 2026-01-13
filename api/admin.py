from django.contrib import admin
from .models import RepairOrder
from vendors.models import VendorProfile
from services.models import Service, ServiceVariant
from users.models import User

# RepairOrder admin
@admin.register(RepairOrder)
class RepairOrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'customer_email', 'vendor_name', 'variant_name', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at', 'vendor']
    search_fields = ['customer__email', 'vendor__business_name', 'variant__name']
    readonly_fields = ['order_id', 'total_amount', 'created_at', 'updated_at']

    def customer_email(self, obj):
        return obj.customer.email
    customer_email.short_description = "Customer Email"

    def vendor_name(self, obj):
        return obj.vendor.business_name
    vendor_name.short_description = "Vendor Name"

    def variant_name(self, obj):
        return obj.variant.name
    variant_name.short_description = "Variant Name"


# Optional: Inline for orders in vendor profile
class RepairOrderInline(admin.TabularInline):
    model = RepairOrder
    extra = 0
    readonly_fields = ['order_id', 'customer', 'variant', 'status', 'total_amount', 'created_at']

@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'user_email', 'is_active', 'created_at']
    search_fields = ['business_name', 'user__email']
    readonly_fields = ['created_at']
    inlines = [RepairOrderInline]

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "User Email"
