from rest_framework import serializers

from .models import Cart, CartItem, Category, Product, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image"]


class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    average_rating = serializers.ReadOnlyField()
    likes_count = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "price",
            "thumbnail",
            "category",
            "average_rating",
            "likes_count",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    images = serializers.SerializerMethodField()
    average_rating = serializers.ReadOnlyField()
    reviews_count = serializers.ReadOnlyField()
    likes_count = serializers.ReadOnlyField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "description",
            "price",
            "images",
            "category",
            "attributes",
            "average_rating",
            "reviews_count",
            "likes_count",
            "is_liked",
            "in_stock",
            "created_at",
            "updated_at",
        ]

    def get_images(self, obj):
        images = obj.images.all()
        if images:
            return [image.image.url for image in images]
        elif obj.thumbnail:
            return [obj.thumbnail.url]
        return []

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.is_liked_by(request.user)
        return False


class CartItemProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "title", "price", "thumbnail"]


class CartItemSerializer(serializers.ModelSerializer):
    product = CartItemProductSerializer(read_only=True)
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = ["product", "quantity", "subtotal"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.ReadOnlyField()
    items_count = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ["items", "total", "items_count"]


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_product_id(self, value):
        try:
            Product.objects.get(id=value, in_stock=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError(
                "Product not found or out of stock"
            )
        return value
