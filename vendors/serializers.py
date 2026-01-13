from rest_framework import serializers
from .models import VendorProfile

class VendorProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")

    class Meta:
        model = VendorProfile
        fields = [
            "id",
            "user",
            "user_email",
            "business_name",
            "address",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "user"]
