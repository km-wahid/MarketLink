# MarketLink

A comprehensive marketplace platform connecting customers with service vendors, featuring cart management, secure payments, and real-time order tracking.

## 🚀 Features

- **Multi-Role Authentication**: Customer, Vendor, and Admin roles with JWT-based security
- **Vendor Management**: Complete vendor profiles with business information
- **Service Catalog**: Flexible service listings with multiple variants
- **Shopping Cart**: Full cart functionality with item management
- **Order Processing**: End-to-end order lifecycle management
- **Stripe Integration**: Secure payment processing with webhook support
- **RESTful API**: Comprehensive API endpoints for all operations

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Models](#database-models)
- [API Documentation](#api-documentation)
- [Stripe Integration](#stripe-integration)
- [Deployment](#deployment)
- [Admin Panel](#admin-panel)
- [Contact](#contact)

## Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)
- Stripe account (for payment processing)

## Installation

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv env

# Activate virtual environment
source env/bin/activate    # macOS/Linux
env\Scripts\activate       # Windows
```

### 2. Install Dependencies

```bash
pip install django djangorestframework djangorestframework-simplejwt python-dotenv stripe djoser
```

### 3. Create Django Project and Apps

```bash
# Create project
django-admin startproject marketlink .

# Create apps
python manage.py startapp users
python manage.py startapp vendors
python manage.py startapp services
python manage.py startapp orders
python manage.py startapp cart
python manage.py startapp payment
```

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Start Development Server

```bash
python manage.py runserver
```

## Configuration

### settings.py

Add the following to your Django settings:

```python
# Stripe Configuration
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

# Add installed apps
INSTALLED_APPS = [
    # ... default apps
    'rest_framework',
    'rest_framework_simplejwt',
    'djoser',
    'users',
    'vendors',
    'services',
    'orders',
    'cart',
    'payment',
]

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}
```

### .env

Create a `.env` file in your project root:

```env
DJANGO_SECRET_KEY=your_django_secret_key_here
STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
```

## Database Models

### User Model

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

### VendorProfile Model

```python
class VendorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255)
    address = models.TextField()
```

### Service & ServiceVariant Models

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

### Cart Models

```python
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ServiceVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
```

### RepairOrder Model

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

## API Documentation

### Authentication

All authenticated endpoints require a JWT token in the header:

```
Authorization: JWT <access_token>
```

#### JWT Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/jwt/create/` | POST | Login and obtain JWT tokens |
| `/auth/jwt/refresh/` | POST | Refresh access token |

### User Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/v1/users/` | GET | List all users | JWT |
| `/api/v1/users/` | POST | Create new user | JWT |
| `/api/v1/users/{id}/` | GET | Retrieve user details | JWT |
| `/api/v1/users/{id}/` | PUT | Update user | JWT |
| `/api/v1/users/{id}/` | DELETE | Delete user | JWT |

### Vendor Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/v1/vendors/` | GET | List all vendors | JWT |
| `/api/v1/vendors/` | POST | Create vendor profile | JWT |
| `/api/v1/vendors/{id}/` | GET | Retrieve vendor details | JWT |
| `/api/v1/vendors/{id}/` | PUT | Update vendor | JWT |
| `/api/v1/vendors/{id}/` | DELETE | Delete vendor | JWT |

### Service Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/v1/services/` | GET | List all services | JWT |
| `/api/v1/services/` | POST | Create new service | JWT |
| `/api/v1/services/{id}/` | GET | Retrieve service details | JWT |
| `/api/v1/services/{id}/` | PUT | Update service | JWT |
| `/api/v1/services/{id}/` | DELETE | Delete service | JWT |
| `/api/v1/service-variants/` | GET | List all service variants | JWT |
| `/api/v1/service-variants/` | POST | Create service variant | JWT |

### Cart Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/v1/carts/` | GET | View user's cart | JWT |
| `/api/v1/cart-items/` | POST | Add item to cart | JWT |
| `/api/v1/cart-items/{id}/` | PUT | Update cart item | JWT |
| `/api/v1/cart-items/{id}/` | DELETE | Remove cart item | JWT |

### Order Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/v1/repair-orders/` | GET | List all orders | JWT |
| `/api/v1/repair-orders/` | POST | Create new order | JWT |
| `/api/v1/customers/{customer_id}/orders/` | GET | Get customer's orders | JWT |
| `/api/v1/vendors/{vendor_id}/orders/` | GET | Get vendor's orders | JWT |

### Payment Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/v1/payments/stripe/checkout/` | POST | Create Stripe PaymentIntent | JWT |
| `/api/v1/payments/stripe/webhook/` | POST | Stripe webhook handler | No |

## Stripe Integration

### Checkout Flow

1. Customer fills their shopping cart
2. Frontend calls `POST /api/v1/payments/stripe/checkout/` with JWT authentication
3. Backend calculates the total amount and creates a Stripe PaymentIntent
4. Backend returns `client_secret` to the frontend
5. Frontend confirms payment using Stripe.js
6. Stripe triggers webhook to `/api/v1/payments/stripe/webhook/`
7. Backend creates RepairOrder and clears the cart

### Stripe Checkout Serializer

```python
class StripeCheckoutSerializer(serializers.Serializer):
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
```

## Deployment

### Local Development with Ngrok

For testing Stripe webhooks locally:

1. Install ngrok:
```bash
pip install pyngrok
```

2. Start ngrok tunnel:
```bash
ngrok http 8000
```

3. Copy the public URL from ngrok dashboard

4. Configure Stripe webhook endpoint:
```
https://<ngrok_id>.ngrok-free.app/api/v1/payments/stripe/webhook/
```

## Admin Panel

Register models in the Django admin panel:

### users/admin.py
```python
from django.contrib import admin
from .models import User

admin.site.register(User)
```

### vendors/admin.py
```python
from django.contrib import admin
from .models import VendorProfile

admin.site.register(VendorProfile)
```

### services/admin.py
```python
from django.contrib import admin
from .models import Service, ServiceVariant

admin.site.register(Service)
admin.site.register(ServiceVariant)
```

### orders/admin.py
```python
from django.contrib import admin
from .models import RepairOrder

admin.site.register(RepairOrder)
```

### cart/admin.py
```python
from django.contrib import admin
from .models import Cart, CartItem

admin.site.register(Cart)
admin.site.register(CartItem)
```

## Serializers

The project includes the following serializers:

- `UserSerializer` - User account serialization
- `VendorProfileSerializer` - Vendor profile data
- `ServiceSerializer` - Service listings
- `ServiceVariantSerializer` - Service variant options
- `CartSerializer` - Shopping cart data
- `CartItemSerializer` - Individual cart items
- `RepairOrderSerializer` - Order information
- `StripeCheckoutSerializer` - Payment processing

## 📝 Features Summary

✅ Complete user authentication system with role-based access  
✅ Vendor profile management  
✅ Service catalog with variants  
✅ Shopping cart functionality  
✅ Order management system  
✅ Stripe payment integration with webhooks  
✅ RESTful API with comprehensive endpoints  
✅ JWT-based security  
✅ Admin panel for system management  

## 🤝 Contact

Portfolio: [https://kmwhid.netlify.app/](https://kmwhid.netlify.app/)

---

**Note**: Remember to never commit your `.env` file or expose your secret keys. Add `.env` to your `.gitignore` file.
