from rest_framework import serializers

from apps.products.models import Product

from .models import Order, OrderItem


class OrderItemProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "title", "price", "thumbnail"]


class OrderItemSerializer(serializers.ModelSerializer):
    product = OrderItemProductSerializer(read_only=True)
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = ["product", "quantity", "price", "subtotal"]


class OrderListSerializer(serializers.ModelSerializer):
    items_count = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "created_at",
            "status",
            "total",
            "items_count",
        ]


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    items_count = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "created_at",
            "updated_at",
            "status",
            "shipping_address",
            "notes",
            "items",
            "subtotal",
            "shipping_fee",
            "total",
            "tracking_number",
            "items_count",
        ]


class CreateOrderSerializer(serializers.Serializer):
    shipping_address = serializers.CharField()
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_shipping_address(self, value):
        if not value.strip():
            raise serializers.ValidationError("Shipping address is required")
        return value
