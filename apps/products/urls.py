from django.urls import path

from . import views

urlpatterns = [
    path("products/", views.product_list, name="product_list"),
    path("products/<int:id>/", views.product_detail, name="product_detail"),
    path("products/<int:id>/like/", views.product_like, name="product_like"),
    path("cart/", views.cart_view, name="cart"),
    path(
        "cart/<int:product_id>/",
        views.remove_from_cart,
        name="remove_from_cart",
    ),
]
