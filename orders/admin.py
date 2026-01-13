from django.contrib import admin
from .models import RepairOrder


@admin.register(RepairOrder)
class RepairOrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_id",
        "customer_email",
        "vendor_name",
        "service_name",
        "variant_name",
        "status",
        "total_amount",
        "created_at",
    )

    list_filter = ("status", "created_at", "vendor")
    search_fields = (
        "order_id",
        "customer__email",
        "vendor__business_name",
        "variant__name",
    )

    readonly_fields = ("order_id", "total_amount", "created_at", "updated_at")

    ordering = ("-created_at",)

    def customer_email(self, obj):
        return obj.customer.email

    def vendor_name(self, obj):
        return obj.vendor.business_name

    def service_name(self, obj):
        return obj.variant.service.name

    def variant_name(self, obj):
        return obj.variant.name

    customer_email.short_description = "Customer"
    vendor_name.short_description = "Vendor"
    service_name.short_description = "Service"
    variant_name.short_description = "Variant"
