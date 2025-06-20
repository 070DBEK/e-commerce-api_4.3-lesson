from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.common.pagination import CustomPageNumberPagination
from apps.common.responses import APIResponse

from .filters import ProductFilter
from .models import Cart, CartItem, Product, ProductLike
from .serializers import (
    AddToCartSerializer,
    CartSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
)


@api_view(["GET"])
@permission_classes([AllowAny])
def product_list(request):
    """List products with filtering and pagination"""
    queryset = Product.objects.filter(in_stock=True).select_related("category")

    # Apply filters
    product_filter = ProductFilter(request.GET, queryset=queryset)
    queryset = product_filter.qs

    # Apply search
    search = request.GET.get("search")
    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )

    # Apply ordering
    sort_field = request.GET.get("sort", "created_at")
    order = request.GET.get("order", "asc")

    if sort_field == "rating":
        # Custom ordering by average rating would require annotation
        pass
    else:
        if order == "desc":
            sort_field = f"-{sort_field}"
        queryset = queryset.order_by(sort_field)

    # Paginate
    paginator = CustomPageNumberPagination()
    page = paginator.paginate_queryset(queryset, request)

    if page is not None:
        serializer = ProductListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    serializer = ProductListSerializer(queryset, many=True)
    return APIResponse.success(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def product_detail(request, id):
    """Get product details"""
    product = get_object_or_404(Product, id=id, in_stock=True)
    serializer = ProductDetailSerializer(product, context={"request": request})
    return APIResponse.success(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def product_like(request, id):
    """Toggle like status for a product"""
    product = get_object_or_404(Product, id=id)

    like, created = ProductLike.objects.get_or_create(
        user=request.user, product=product
    )

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    return APIResponse.success(
        {"liked": liked, "likes_count": product.likes_count}
    )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def cart_view(request):
    """View cart or add to cart"""
    cart, created = Cart.objects.get_or_create(user=request.user)

    if request.method == "GET":
        serializer = CartSerializer(cart)
        return APIResponse.success(serializer.data)

    elif request.method == "POST":
        serializer = AddToCartSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data["product_id"]
            quantity = serializer.validated_data["quantity"]

            product = Product.objects.get(id=product_id)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, product=product, defaults={"quantity": quantity}
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            cart_serializer = CartSerializer(cart)
            return APIResponse.success(cart_serializer.data)

        return APIResponse.error("Invalid request", details=serializer.errors)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, product_id):
    """Remove product from cart"""
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)

    cart_item.delete()

    cart_serializer = CartSerializer(cart)
    return APIResponse.success(cart_serializer.data)
