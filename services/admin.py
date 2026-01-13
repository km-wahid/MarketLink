from django.contrib import admin
from .models import Service, ServiceVariant
from vendors.models import VendorProfile

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ["name", "vendor", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name", "vendor__business_name"]

@admin.register(ServiceVariant)
class ServiceVariantAdmin(admin.ModelAdmin):
    list_display = ["name", "service", "price", "stock"]
    list_filter = ["service"]
    search_fields = ["name", "service__name"]
