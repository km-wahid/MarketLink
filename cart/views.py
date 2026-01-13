# carts/views.py
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from services.models import ServiceVariant

class CartViewSet(ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if self.request.user.role != "customer":
            raise PermissionDenied("Only customers can have a cart")
        serializer.save(user=self.request.user)


class CartItemViewSet(ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != "customer":
            raise PermissionDenied("Only customers can add to cart")

        cart, _ = Cart.objects.get_or_create(user=user)
        variant = serializer.validated_data["variant"]
        qty = serializer.validated_data["quantity"]

        item, created = CartItem.objects.get_or_create(cart=cart, variant=variant)

        if not created:
            item.quantity += qty
            item.save()
        else:
            item.quantity = qty
            item.save()

        serializer.instance = item
