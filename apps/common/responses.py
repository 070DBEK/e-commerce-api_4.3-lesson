from rest_framework import status
from rest_framework.response import Response


class APIResponse:
    @staticmethod
    def success(data=None, message=None, status_code=status.HTTP_200_OK):
        response_data = {"success": True}
        if data is not None:
            response_data["data"] = data
        if message:
            response_data["message"] = message
        return Response(response_data, status=status_code)

    @staticmethod
    def error(
        message,
        code=None,
        details=None,
        status_code=status.HTTP_400_BAD_REQUEST,
    ):
        response_data = {"success": False, "error": {"message": message}}
        if code:
            response_data["error"]["code"] = code
        if details:
            response_data["error"]["details"] = details
        return Response(response_data, status=status_code)
