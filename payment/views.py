from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from decimal import Decimal
from cart.models import Cart
from orders.models import RepairOrder
import stripe
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from django.http import JsonResponse
from orders.models import RepairOrder

from users.models import User

class StripeCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY  # ✅ set here

        user = request.user
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({"error": "Cart is empty"}, status=400)

        if not cart.items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        total = 0
        line_items = []

        for item in cart.items.all():
            total += item.variant.price * item.quantity
            line_items.append({
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": item.variant.name},
                    "unit_amount": int(item.variant.price * 100),
                },
                "quantity": item.quantity
            })

        intent = stripe.PaymentIntent.create(
            amount=int(total * 100),
            currency="usd",
            metadata={"user_id": str(user.id)},
        )

        return Response({"client_secret": intent.client_secret})

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET  # store this in .env

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return JsonResponse({"error": "Invalid payload"}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({"error": "Invalid signature"}, status=400)

    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        user_id = intent.metadata.user_id
        user = User.objects.get(id=user_id)
        cart = Cart.objects.get(user=user)

        with transaction.atomic():
            for item in cart.items.all():
                RepairOrder.objects.create(
                    customer=user,
                    vendor=item.variant.service.vendor,
                    variant=item.variant,
                    total_amount=item.variant.price * item.quantity,
                    status="paid"
                )
                item.variant.stock -= item.quantity
                item.variant.save()
            cart.items.all().delete()

    return JsonResponse({"status": "success"}, status=200)