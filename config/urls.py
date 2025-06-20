from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.common.views import sms_callback

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.users.urls")),
    path("api/v1/shop/", include("apps.products.urls")),
    path("api/v1/shop/", include("apps.orders.urls")),
    path("api/v1/shop/", include("apps.reviews.urls")),
    path("api/v1/sms/callback/", sms_callback, name="sms_callback"),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
