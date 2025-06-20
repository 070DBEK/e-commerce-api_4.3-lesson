from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["subtotal"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "order_number",
        "user",
        "status",
        "total",
        "items_count",
        "created_at",
    ]
    list_filter = ["status", "created_at"]
    search_fields = ["order_number", "user__phone", "user__name"]
    inlines = [OrderItemInline]
    readonly_fields = [
        "order_number",
        "created_at",
        "updated_at",
        "items_count",
    ]

    fieldsets = (
        (
            "Order Information",
            {"fields": ("order_number", "user", "status", "tracking_number")},
        ),
        ("Shipping", {"fields": ("shipping_address", "notes")}),
        ("Pricing", {"fields": ("subtotal", "shipping_fee", "total")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "product", "quantity", "price", "subtotal"]
    list_filter = ["order__status", "order__created_at"]
    search_fields = ["order__order_number", "product__title"]
    readonly_fields = ["subtotal"]
