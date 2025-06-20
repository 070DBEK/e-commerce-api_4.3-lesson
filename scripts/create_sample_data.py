#!/usr/bin/env python
"""
Script to create sample data for the e-commerce API
"""
import os
import sys

import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from decimal import Decimal

from django.contrib.auth import get_user_model

from apps.orders.models import Order, OrderItem
from apps.products.models import Category, Product
from apps.reviews.models import Review

User = get_user_model()


def create_sample_data():
    print("Creating sample data...")

    # Create categories
    categories_data = [
        {"name": "Electronics", "slug": "electronics"},
        {"name": "Clothing", "slug": "clothing"},
        {"name": "Books", "slug": "books"},
        {"name": "Home & Garden", "slug": "home-garden"},
        {"name": "Sports", "slug": "sports"},
    ]

    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(**cat_data)
        categories.append(category)
        if created:
            print(f"Created category: {category.name}")

    # Create products
    products_data = [
        {
            "title": "iPhone 15 Pro",
            "description": "Latest iPhone with advanced features",
            "price": Decimal("999.99"),
            "category": categories[0],  # Electronics
            "attributes": {"color": "Space Black", "storage": "256GB"},
        },
        {
            "title": "Samsung Galaxy S24",
            "description": "Flagship Android smartphone",
            "price": Decimal("899.99"),
            "category": categories[0],  # Electronics
            "attributes": {"color": "Phantom Black", "storage": "128GB"},
        },
        {
            "title": "Premium Cotton T-Shirt",
            "description": "High-quality cotton t-shirt, perfect for everyday wear",
            "price": Decimal("29.99"),
            "category": categories[1],  # Clothing
            "attributes": {
                "color": "blue",
                "size": "L",
                "material": "100% cotton",
            },
        },
        {
            "title": "Wireless Headphones",
            "description": "Noise-cancelling wireless headphones",
            "price": Decimal("199.99"),
            "category": categories[0],  # Electronics
            "attributes": {"color": "Black", "wireless": True},
        },
        {
            "title": "Programming Book",
            "description": "Learn Python programming from scratch",
            "price": Decimal("49.99"),
            "category": categories[2],  # Books
            "attributes": {"pages": 500, "language": "English"},
        },
    ]

    products = []
    for prod_data in products_data:
        product, created = Product.objects.get_or_create(
            title=prod_data["title"], defaults=prod_data
        )
        products.append(product)
        if created:
            print(f"Created product: {product.title}")

    # Create sample users
    users_data = [
        {
            "phone": "+998901111111",
            "name": "John Doe",
            "password": "testpass123",
        },
        {
            "phone": "+998902222222",
            "name": "Jane Smith",
            "password": "testpass123",
        },
    ]

    users = []
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            phone=user_data["phone"], defaults={"name": user_data["name"]}
        )
        if created:
            user.set_password(user_data["password"])
            user.save()
            print(f"Created user: {user.phone}")
        users.append(user)

    # Create sample orders
    if users and products:
        order, created = Order.objects.get_or_create(
            user=users[0],
            defaults={
                "shipping_address": "123 Main St, Tashkent, Uzbekistan",
                "notes": "Please deliver after 6 PM",
                "subtotal": Decimal("1029.98"),
                "shipping_fee": Decimal("5.00"),
                "total": Decimal("1034.98"),
                "status": "delivered",
            },
        )

        if created:
            # Create order items
            OrderItem.objects.create(
                order=order,
                product=products[0],  # iPhone
                quantity=1,
                price=products[0].price,
            )
            OrderItem.objects.create(
                order=order,
                product=products[2],  # T-Shirt
                quantity=1,
                price=products[2].price,
            )
            print(f"Created order: {order.order_number}")

            # Create sample reviews
            Review.objects.create(
                user=users[0],
                product=products[0],
                rating=5,
                comment="Great product, very satisfied with the quality!",
            )
            Review.objects.create(
                user=users[0],
                product=products[2],
                rating=4,
                comment="Good quality t-shirt, fits well.",
            )
            print("Created sample reviews")

    print("Sample data creation completed!")


if __name__ == "__main__":
    create_sample_data()
