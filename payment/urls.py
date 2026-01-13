from django.urls import path
from .views import StripeCheckoutView, stripe_webhook

urlpatterns = [
    path("stripe/checkout/", StripeCheckoutView.as_view(), name="stripe-checkout"),
    path("stripe/webhook/", stripe_webhook, name="stripe-webhook"),
]
