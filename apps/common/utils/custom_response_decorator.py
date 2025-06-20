from functools import wraps

from rest_framework import status
from rest_framework.response import Response


def api_response(success_message=None, error_message=None):
    """
    API response decorator for consistent response format
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            try:
                result = view_func(*args, **kwargs)

                # If it's already a Response object, return as is
                if isinstance(result, Response):
                    return result

                # If it's a tuple (data, status_code)
                if isinstance(result, tuple) and len(result) == 2:
                    data, status_code = result
                    response_data = {"success": True, "data": data}
                    if success_message:
                        response_data["message"] = success_message
                    return Response(response_data, status=status_code)

                # If it's just data
                response_data = {"success": True, "data": result}
                if success_message:
                    response_data["message"] = success_message

                return Response(response_data, status=status.HTTP_200_OK)

            except Exception as e:
                response_data = {
                    "success": False,
                    "error": {"message": error_message or str(e)},
                }
                return Response(
                    response_data, status=status.HTTP_400_BAD_REQUEST
                )

        return wrapper

    return decorator


class APIResponseMixin:
    """Mixin for consistent API responses"""

    def success_response(
        self, data=None, message=None, status_code=status.HTTP_200_OK
    ):
        """Success response helper"""
        response_data = {"success": True}
        if data is not None:
            response_data["data"] = data
        if message:
            response_data["message"] = message
        return Response(response_data, status=status_code)

    def error_response(
        self, message, details=None, status_code=status.HTTP_400_BAD_REQUEST
    ):
        """Error response helper"""
        response_data = {"success": False, "error": {"message": message}}
        if details:
            response_data["error"]["details"] = details
        return Response(response_data, status=status_code)
