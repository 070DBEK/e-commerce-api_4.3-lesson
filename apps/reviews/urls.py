from django.urls import path

from . import views

urlpatterns = [
    path(
        "products/<int:id>/review/", views.create_review, name="create_review"
    ),
]
