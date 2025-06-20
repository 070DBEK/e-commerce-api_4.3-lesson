from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, VerificationCode


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["phone", "name", "email", "is_active", "date_joined"]
    list_filter = ["is_active", "is_staff", "date_joined"]
    search_fields = ["phone", "name", "email"]
    ordering = ["-date_joined"]

    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        (
            "Personal info",
            {"fields": ("name", "email", "default_shipping_address")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone", "password1", "password2"),
            },
        ),
    )


@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ["phone", "code", "is_used", "expires_at", "created_at"]
    list_filter = ["is_used", "created_at"]
    search_fields = ["phone"]
    readonly_fields = ["created_at", "updated_at"]
