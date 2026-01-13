from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("variant", "quantity")
    can_delete = True


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user_email", "item_count", "created_at")
    inlines = [CartItemInline]
    search_fields = ("user__email",)
    readonly_fields = ("created_at",)

    def user_email(self, obj):
        return obj.user.email

    def item_count(self, obj):
        return obj.items.count()

    user_email.short_description = "Customer"
    item_count.short_description = "Items"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart_user", "variant_name", "quantity")
    search_fields = ("cart__user__email", "variant__name")

    def cart_user(self, obj):
        return obj.cart.user.email

    def variant_name(self, obj):
        return obj.variant.name
