from rest_framework import serializers
from .models import RepairOrder
from services.models import ServiceVariant

class RepairOrderSerializer(serializers.ModelSerializer):
    customer_email = serializers.ReadOnlyField(source="customer.email")
    vendor_name = serializers.ReadOnlyField(source="vendor.business_name")
    variant_name = serializers.ReadOnlyField(source="variant.name")

    class Meta:
        model = RepairOrder
        fields = [
            "id",
            "order_id",
            "customer",
            "customer_email",
            "vendor",
            "vendor_name",
            "variant",
            "variant_name",
            "status",
            "total_amount",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "order_id", "customer", "vendor", "total_amount", "created_at", "updated_at"]

    def validate_variant(self, value):
        if not value.service.is_active:
            raise serializers.ValidationError("The selected service is not active.")
        if not value.service.vendor.is_active:
            raise serializers.ValidationError("The vendor for this service is not active.")
        return value
