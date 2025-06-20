import logging

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([AllowAny])
def sms_callback(request):
    """Eskiz SMS callback handler"""
    try:
        data = request.data
        message_id = data.get("id")
        sms_status = data.get("status")

        # Log SMS status
        logger.info(f"SMS callback: ID={message_id}, Status={sms_status}")

        # Bu yerda SMS holatini database da yangilash mumkin
        # Masalan, SMSLog modelini yaratib, holatlarni saqlash

        return Response({"success": True}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"SMS callback error: {e}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
