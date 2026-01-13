# MarketLink – Project Documentation

## 1. Project Overview

**MarketLink** is a marketplace platform where customers can browse and order services from vendors. It supports:

- User registration (Customer, Vendor, Admin)
- Vendor profiles
- Services & variants
- Cart & order management
- Stripe checkout with webhook
- JWT-based authentication

---

## 2. Setup Instructions

### 2.1 Create Project & Virtual Environment

```bash
python -m venv env
source env/bin/activate    # macOS/Linux
env\Scripts\activate       # Windows
pip install django djangorestframework djangorestframework-simplejwt python-dotenv stripe djoser
django-admin startproject marketlink .
python manage.py startapp users
python manage.py startapp vendors
python manage.py startapp services
python manage.py startapp orders
python manage.py startapp cart
python manage.py startapp payment
```

### 2.2 Settings Configuration

**settings.py**

```python


# Stripe keys
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")
```

**.env**

```env
DJANGO_SECRET_KEY=your_django_secret
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
```

---

## 3. Models Overview

### 3.1 Users

```python
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('admin', 'Admin')
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
```

### 3.2 VendorProfile

```python
class VendorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255)
    address = models.TextField()
```

### 3.3 Services

```python
class Service(models.Model):
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=255)
    description = models.TextField()
    is_active = models.BooleanField(default=True)

class ServiceVariant(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="variants")
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_minutes = models.IntegerField()
    stock = models.IntegerField()
```

### 3.4 Orders

```python
class RepairOrder(models.Model):
    order_id = models.UUIDField(default=uuid.uuid4, unique=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE)
    variant = models.ForeignKey(ServiceVariant, on_delete=models.PROTECT)
    status = models.CharField(
        max_length=20,
        choices=(
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('completed', 'Completed')
        )
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
```

### 3.5 Cart

```python
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ServiceVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
```

---

## 4. Serializers

The project includes the following serializers:

- `UserSerializer`
- `VendorProfileSerializer`
- `ServiceSerializer`
- `ServiceVariantSerializer`
- `CartSerializer`
- `CartItemSerializer`
- `RepairOrderSerializer`

**Example for Stripe checkout:**

```python
class StripeCheckoutSerializer(serializers.Serializer):
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
```

---

## 5. Views & API

### 5.1 JWT Authentication

- **Login:** `POST /auth/jwt/create/`
- **Refresh:** `POST /auth/jwt/refresh/`
- **Headers:** `Authorization: JWT <access_token>`

### 5.2 User Endpoints

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/v1/users/` | GET, POST | List or create user | JWT |
| `/api/v1/users/{id}/` | GET, PUT, DELETE | User detail | JWT |

### 5.3 Vendor Endpoints

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/v1/vendors/` | GET, POST | List or create vendor profile | JWT |
| `/api/v1/vendors/{id}/` | GET, PUT, DELETE | Vendor detail | JWT |

### 5.4 Services

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/v1/services/` | GET, POST | List or create service | JWT |
| `/api/v1/services/{id}/` | GET, PUT, DELETE | Service detail | JWT |
| `/api/v1/service-variants/` | GET, POST | List or create variant | JWT |

### 5.5 Cart

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/v1/carts/` | GET | View user's cart | JWT |
| `/api/v1/cart-items/` | POST | Add item to cart | JWT |
| `/api/v1/cart-items/{id}/` | PUT, DELETE | Update/remove item | JWT |

### 5.6 Orders

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/v1/repair-orders/` | GET, POST | List or create repair order | JWT |
| `/api/v1/customers/{customer_id}/orders/` | GET | Customer-specific orders | JWT |
| `/api/v1/vendors/{vendor_id}/orders/` | GET | Vendor-specific orders | JWT |

### 5.7 Stripe Checkout

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/v1/payments/stripe/checkout/` | POST | Create Stripe PaymentIntent for cart | JWT |
| `/api/v1/payments/stripe/webhook/` | POST | Webhook for Stripe events | No Auth |

---

## 6. Stripe Checkout Flow

1. Customer fills cart
2. Frontend calls `POST /api/v1/payments/stripe/checkout/` with JWT
3. Backend calculates total and creates PaymentIntent
4. Backend returns `client_secret`
5. Frontend confirms payment using Stripe.js
6. Stripe triggers webhook: `/api/v1/payments/stripe/webhook/`
7. Backend creates RepairOrder and clears cart

---

## 7. Deployment with Ngrok

```bash
pip install pyngrok
ngrok http 8000
```

Get public URL from ngrok dashboard and set webhook URL in Stripe to:

```
https://<ngrok_id>.ngrok-free.app/api/v1/payments/stripe/webhook/
```

---

## 8. Admin Registration

**users/admin.py**

```python
from django.contrib import admin
from .models import User
admin.site.register(User)
```

**vendors/admin.py**

```python
from django.contrib import admin
from .models import VendorProfile
admin.site.register(VendorProfile)
```

**services/admin.py**

```python
from django.contrib import admin
from .models import Service, ServiceVariant
admin.site.register(Service)
admin.site.register(ServiceVariant)
```

**orders/admin.py**

```python
from django.contrib import admin
from .models import RepairOrder
admin.site.register(RepairOrder)
```

**cart/admin.py**

```python
from django.contrib import admin
from .models import Cart, CartItem
admin.site.register(Cart)
admin.site.register(CartItem)
```

---

## ✅ Features Summary

Now you have:

- Models, serializers, views
- JWT authentication
- Cart & orders
- Stripe checkout & webhook
- Full API endpoint table
- Ngrok setup for webhooks
- Admin panel registrations

---



## Contact

[https://kmwhid.netlify.app/]
