from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["user", "product", "rating", "created_at"]
    list_filter = ["rating", "created_at"]
    search_fields = ["user__phone", "user__name", "product__title"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (
            "Review Information",
            {"fields": ("user", "product", "rating", "comment")},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
