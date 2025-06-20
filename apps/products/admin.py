from django.contrib import admin

from .models import (
    Cart,
    CartItem,
    Category,
    Product,
    ProductImage,
    ProductLike,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "created_at"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "price", "in_stock", "created_at"]
    list_filter = ["category", "in_stock", "created_at"]
    search_fields = ["title", "description"]
    inlines = [ProductImageInline]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(ProductLike)
class ProductLikeAdmin(admin.ModelAdmin):
    list_display = ["user", "product", "created_at"]
    list_filter = ["created_at"]


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["user", "items_count", "total", "created_at"]
    inlines = [CartItemInline]
    readonly_fields = ["created_at", "updated_at"]
