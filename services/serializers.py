from rest_framework import serializers
from .models import Service, ServiceVariant


class ServiceVariantSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)  # for updates
    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(),
        required=True,
        write_only=True
    )
    service_name = serializers.ReadOnlyField(source="service.name")  # optional for response

    class Meta:
        model = ServiceVariant
        fields = ["id", "service", "service_name", "name", "price", "estimated_minutes", "stock"]


class ServiceSerializer(serializers.ModelSerializer):
    variants = ServiceVariantSerializer(many=True, required=False)

    class Meta:
        model = Service
        fields = ["id", "name", "description", "is_active", "variants", "vendor"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        variants_data = validated_data.pop("variants", [])
        service = Service.objects.create(**validated_data)

        for variant_data in variants_data:
            ServiceVariant.objects.create(service=service, **variant_data)

        return service

    def update(self, instance, validated_data):
        variants_data = validated_data.pop("variants", None)

        instance.name = validated_data.get("name", instance.name)
        instance.description = validated_data.get("description", instance.description)
        instance.is_active = validated_data.get("is_active", instance.is_active)
        # Allow admin to change vendor
        if "vendor" in validated_data:
            instance.vendor = validated_data["vendor"]
        instance.save()

        if variants_data is not None:
            # Remove old variants and add new ones
            instance.variants.all().delete()
            for variant_data in variants_data:
                ServiceVariant.objects.create(service=instance, **variant_data)

        return instance
