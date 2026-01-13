from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import RepairOrder
from .serializers import RepairOrderSerializer

class RepairOrderViewSet(ModelViewSet):
    serializer_class = RepairOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "customer":
            # Customers can see only their own orders
            return RepairOrder.objects.filter(customer=user)
        elif user.role == "vendor":
            # Vendors can see only their orders
            return RepairOrder.objects.filter(vendor__user=user)
        elif user.role == "admin":
            return RepairOrder.objects.all()
        else:
            return RepairOrder.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != "customer":
            raise PermissionDenied("Only customers can create repair orders.")

        variant = serializer.validated_data["variant"]

        # automatically attach vendor from the ServiceVariant
        vendor = variant.service.vendor

        # total_amount = variant price
        total_amount = variant.price

        serializer.save(customer=user, vendor=vendor, total_amount=total_amount)
