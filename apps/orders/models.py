import uuid

from django.contrib.auth import get_user_model
from django.db import models

from apps.common.models import BaseModel
from apps.products.models import Product

User = get_user_model()


class Order(BaseModel):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="orders"
    )
    order_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    shipping_address = models.TextField()
    notes = models.TextField(blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=5.00
    )
    total = models.DecimalField(max_digits=10, decimal_places=2)
    tracking_number = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.order_number

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if not self.order_number:
            self.order_number = self.generate_order_number()
        if not self.total:
            self.total = self.subtotal + self.shipping_fee

        super().save(*args, **kwargs)

        # Send SMS notification for new orders
        if is_new:
            from apps.common.utils import send_order_notification_async

            send_order_notification_async.delay(
                self.user.phone, self.order_number
            )

    def generate_order_number(self):
        from datetime import datetime

        date_str = datetime.now().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"ORD-{date_str}-{unique_id}"

    @property
    def items_count(self):
        return sum(item.quantity for item in self.items.all())


class OrderItem(BaseModel):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product.title}"

    @property
    def subtotal(self):
        return self.price * self.quantity

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.product.price
        super().save(*args, **kwargs)
