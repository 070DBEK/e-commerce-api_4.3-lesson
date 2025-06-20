import logging

from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """Custom exception handler for DRF"""

    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        custom_response_data = {
            "success": False,
            "error": {
                "message": "Xatolik yuz berdi",
                "details": response.data,
            },
        }

        # Log the error
        logger.error(f"API Error: {exc}", exc_info=True)

        # Customize error messages based on status code
        if response.status_code == 400:
            custom_response_data["error"][
                "message"
            ] = "Noto'g'ri ma'lumot yuborildi"
        elif response.status_code == 401:
            custom_response_data["error"][
                "message"
            ] = "Avtorizatsiya talab qilinadi"
        elif response.status_code == 403:
            custom_response_data["error"]["message"] = "Ruxsat berilmagan"
        elif response.status_code == 404:
            custom_response_data["error"]["message"] = "Ma'lumot topilmadi"
        elif response.status_code == 405:
            custom_response_data["error"][
                "message"
            ] = "Metod ruxsat berilmagan"
        elif response.status_code == 429:
            custom_response_data["error"][
                "message"
            ] = "Juda ko'p so'rov yuborildi"
        elif response.status_code >= 500:
            custom_response_data["error"]["message"] = "Server xatosi"
            # Don't expose internal error details in production
            if (
                not hasattr(context.get("request"), "user")
                or not context["request"].user.is_staff
            ):
                custom_response_data["error"][
                    "details"
                ] = "Ichki server xatosi"

        response.data = custom_response_data

    return response
