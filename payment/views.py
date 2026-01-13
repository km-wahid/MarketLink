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
from rest_framework.exceptions import ValidationError
from django.http import JsonResponse
from orders.models import RepairOrder
from common.redis import redis_client
from users.models import User

class StripeCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        user = request.user
        cart = Cart.objects.get(user=user)

        for item in cart.items.all():
            lock_key = f"lock:variant:{item.variant.id}"
            lock = redis_client.lock(lock_key, timeout=10)

            if not lock.acquire(blocking=False):
                raise ValidationError("This service is currently being booked. Try again.")

            try:
                with transaction.atomic():
                    item.variant.refresh_from_db()

                    if item.variant.stock < item.quantity:
                        raise ValidationError("Service sold out")

                    item.variant.stock -= item.quantity
                    item.variant.save()

            finally:
                lock.release()


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