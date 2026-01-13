import paypalrestsdk
from decimal import Decimal
from cart.models import Cart
from orders.models import RepairOrder
from django.conf import settings


def create_paypal_payment(cart: Cart, return_url, cancel_url):
    items = []
    total = Decimal("0.00")

    for item in cart.items.all():
        price = item.product.variant.price
        qty = item.quantity
        total += price * qty

        items.append({
            "name": item.product.variant.name,
            "sku": str(item.product.id),
            "price": str(price),
            "currency": "USD",
            "quantity": qty
        })

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "redirect_urls": {
            "return_url": return_url,
            "cancel_url": cancel_url
        },
        "transactions": [{
            "item_list": {"items": items},
            "amount": {
                "total": str(total),
                "currency": "USD"
            },
            "description": "Service Booking Payment"
        }]
    })

    if payment.create():
        return payment
    else:
        raise Exception(payment.error)
