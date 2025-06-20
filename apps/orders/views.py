from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from apps.common.pagination import CustomPageNumberPagination
from apps.common.responses import APIResponse
from apps.products.models import Cart

from .models import Order, OrderItem
from .serializers import (
    CreateOrderSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def orders_view(request):
    """List orders or create new order"""
    if request.method == "GET":
        queryset = Order.objects.filter(user=request.user)

        # Filter by status if provided
        status_filter = request.GET.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Paginate
        paginator = CustomPageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = OrderListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = OrderListSerializer(queryset, many=True)
        return APIResponse.success(serializer.data)

    elif request.method == "POST":
        serializer = CreateOrderSerializer(data=request.data)
        if serializer.is_valid():
            # Get user's cart
            try:
                cart = Cart.objects.get(user=request.user)
                if not cart.items.exists():
                    return APIResponse.error("Cart is empty")
            except Cart.DoesNotExist:
                return APIResponse.error("Cart is empty")

            with transaction.atomic():
                # Create order
                order = Order.objects.create(
                    user=request.user,
                    shipping_address=serializer.validated_data[
                        "shipping_address"
                    ],
                    notes=serializer.validated_data.get("notes", ""),
                    subtotal=cart.total,
                    total=cart.total + 5.00,  # Add shipping fee
                )

                # Create order items from cart
                for cart_item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        price=cart_item.product.price,
                    )

                # Clear cart
                cart.items.all().delete()

            order_serializer = OrderDetailSerializer(order)
            return APIResponse.success(
                order_serializer.data, status_code=status.HTTP_201_CREATED
            )

        return APIResponse.error("Invalid request", details=serializer.errors)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def order_detail(request, id):
    """Get order details"""
    order = get_object_or_404(Order, id=id, user=request.user)
    serializer = OrderDetailSerializer(order)
    return APIResponse.success(serializer.data)
