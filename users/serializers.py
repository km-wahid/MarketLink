from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "address",
            "role",
            "is_active",
            "date_joined",
        ]
        read_only_fields = ["id", "role", "is_active", "date_joined"]

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    want_to_be_vendor = serializers.BooleanField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "first_name",
            "last_name",
            "phone_number",
            "address",
            'want_to_be_vendor'
        ]

    def create(self, validated_data):
        want_vendor = validated_data.pop("want_to_be_vendor", False)
        password = validated_data.pop("password")

        user = User.objects.create_user(**validated_data)
        user.set_password(password)

        if want_vendor:
            user.is_vendor_requested = True  # Request submitted

        user.save()
        return user
