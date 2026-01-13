from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import VendorProfile
from .serializers import VendorProfileSerializer
from .permission import IsVendor

class VendorProfileViewSet(ModelViewSet):
    serializer_class = VendorProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return VendorProfile.objects.all()
        if user.role == "vendor":
            return VendorProfile.objects.filter(user=user)
        return VendorProfile.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
