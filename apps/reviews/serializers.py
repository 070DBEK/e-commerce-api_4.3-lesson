from rest_framework import serializers

from apps.orders.models import OrderItem

from .models import Review


class ReviewUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class ReviewSerializer(serializers.ModelSerializer):
    user = ReviewUserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "product_id",
            "user",
            "rating",
            "comment",
            "created_at",
        ]
        read_only_fields = ["id", "product_id", "user", "created_at"]

    def validate(self, attrs):
        user = self.context["request"].user
        product_id = self.context["product_id"]

        # Check if user has purchased this product
        has_purchased = OrderItem.objects.filter(
            order__user=user,
            product_id=product_id,
            order__status__in=["delivered", "processing", "shipped"],
        ).exists()

        if not has_purchased:
            raise serializers.ValidationError(
                "You can only review products you have purchased"
            )

        # Check if user has already reviewed this product
        if Review.objects.filter(user=user, product_id=product_id).exists():
            raise serializers.ValidationError(
                "You have already reviewed this product"
            )

        return attrs

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        validated_data["product_id"] = self.context["product_id"]
        return super().create(validated_data)
