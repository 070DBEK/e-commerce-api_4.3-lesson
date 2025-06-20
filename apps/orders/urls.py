from django.urls import path

from . import views

urlpatterns = [
    path("orders/", views.orders_view, name="orders"),
    path("orders/<int:id>/", views.order_detail, name="order_detail"),
]
