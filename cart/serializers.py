# carts/serializers.py
from rest_framework import serializers
from .models import Cart, CartItem
from services.models import ServiceVariant

class CartItemSerializer(serializers.ModelSerializer):
    variant_name = serializers.ReadOnlyField(source="variant.name")
    price = serializers.ReadOnlyField(source="variant.price")
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "variant", "variant_name", "price", "quantity", "subtotal"]

    def get_subtotal(self, obj):
        return obj.variant.price * obj.quantity


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "items", "total", "created_at"]

    def get_total(self, cart):
        return sum(item.variant.price * item.quantity for item in cart.items.all())
