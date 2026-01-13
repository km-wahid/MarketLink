from django.urls import path, include
from rest_framework_nested import routers
from users.views import UserViewSet
from vendors.views import VendorProfileViewSet
from orders.views import RepairOrderViewSet
from cart.views import CartViewSet, CartItemViewSet

router = routers.DefaultRouter()
router.register('customers', UserViewSet, basename='customer')
router.register('vendors', VendorProfileViewSet, basename='vendor')
router.register('repair-orders', RepairOrderViewSet, basename='repair-order')

# Nested router for customer orders
customer_router = routers.NestedDefaultRouter(router, 'customers', lookup='customer')
customer_router.register('orders', RepairOrderViewSet, basename='customer-orders')

# Nested router for vendor orders
vendor_router = routers.NestedDefaultRouter(router, 'vendors', lookup='vendor')
vendor_router.register('orders', RepairOrderViewSet, basename='vendor-orders')

router.register("carts", CartViewSet, basename="cart")
router.register("cart-items", CartItemViewSet, basename="cart-items")

urlpatterns = [
    path('', include(router.urls)),
    path('', include(customer_router.urls)),
    path('', include(vendor_router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path("payments/", include("payment.urls")),

]
