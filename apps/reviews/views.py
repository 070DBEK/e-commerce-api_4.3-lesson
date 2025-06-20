from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from apps.common.responses import APIResponse
from apps.products.models import Product

from .serializers import ReviewSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_review(request, id):
    """Create a review for a product"""
    product = get_object_or_404(Product, id=id)

    serializer = ReviewSerializer(
        data=request.data, context={"request": request, "product_id": id}
    )

    if serializer.is_valid():
        review = serializer.save()
        return APIResponse.success(
            ReviewSerializer(review).data, status_code=status.HTTP_201_CREATED
        )

    return APIResponse.error("Invalid request", details=serializer.errors)
