from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Service, ServiceVariant
from .serializers import ServiceSerializer, ServiceVariantSerializer
from .permission import IsVendorOrAdmin
from vendors.models import VendorProfile

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Service
from .serializers import ServiceSerializer
from vendors.models import VendorProfile



class ServiceViewSet(ModelViewSet):
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "admin":
            return Service.objects.all()

        if user.role == "vendor":
            return Service.objects.filter(vendor__user=user)

        # customers cannot access
        return Service.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if user.role == "admin":
            vendor_id = self.request.data.get("vendor")
            if not vendor_id:
                raise PermissionDenied("Admin must provide a vendor ID")
            try:
                vendor = VendorProfile.objects.get(id=vendor_id)
            except VendorProfile.DoesNotExist:
                raise PermissionDenied("Vendor with this ID does not exist")
            serializer.save(vendor=vendor)

        elif user.role == "vendor":
            try:
                vendor = VendorProfile.objects.get(user=user)
            except VendorProfile.DoesNotExist:
                raise PermissionDenied("Vendor profile not found. Please create your VendorProfile first.")
            serializer.save(vendor=vendor)

        else:
            raise PermissionDenied("You do not have permission to create a service")


class ServiceVariantViewSet(ModelViewSet):
    serializer_class = ServiceVariantSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "admin":
            return ServiceVariant.objects.all()

        if user.role == "vendor":
            return ServiceVariant.objects.filter(service__vendor__user=user)

        return ServiceVariant.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        service_id = self.request.data.get("service")

        if not service_id:
            raise PermissionDenied("You must provide a service ID")

        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            raise PermissionDenied("Service with this ID does not exist")

        if user.role == "admin":
            # Admin can attach to any service
            serializer.save(service=service)

        elif user.role == "vendor":
            # Vendor can only attach variants to their own services
            if service.vendor.user != user:
                raise PermissionDenied("You cannot add variant to this service")
            serializer.save(service=service)

        else:
            raise PermissionDenied("You do not have permission to create variants")