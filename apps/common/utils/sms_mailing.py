import logging
from typing import Any, Dict, Optional

import requests
from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)


class EskizSMSService:
    """Eskiz SMS xizmati uchun klass"""

    def __init__(self):
        self.base_url = "https://notify.eskiz.uz/api"
        self.email = settings.ESKIZ_EMAIL
        self.password = settings.ESKIZ_PASSWORD
        self.token = None

    def get_token(self) -> Optional[str]:
        """Eskiz SMS dan token olish"""
        try:
            url = f"{self.base_url}/auth/login"
            data = {"email": self.email, "password": self.password}

            response = requests.post(url, data=data)
            response.raise_for_status()

            result = response.json()
            if result.get("message") == "token_generated":
                self.token = result["data"]["token"]
                return self.token
            else:
                logger.error(f"Token olishda xatolik: {result}")
                return None

        except requests.RequestException as e:
            logger.error(f"Eskiz SMS token olishda xatolik: {e}")
            return None

    def send_sms(self, phone: str, message: str) -> Dict[str, Any]:
        """SMS yuborish"""
        try:
            # Token olish
            if not self.token:
                self.get_token()

            if not self.token:
                return {"success": False, "error": "Token olishda xatolik"}

            # Telefon raqamini formatlash
            if phone.startswith("+"):
                phone = phone[1:]

            url = f"{self.base_url}/message/sms/send"
            headers = {"Authorization": f"Bearer {self.token}"}
            data = {
                "mobile_phone": phone,
                "message": message,
                "from": "4546",  # Eskiz SMS dan berilgan sender ID
                "callback_url": f"{settings.BASE_URL}/api/v1/sms/callback/",
            }

            response = requests.post(url, headers=headers, data=data)

            if response.status_code == 401:
                # Token muddati tugagan, yangi token olish
                self.get_token()
                if self.token:
                    headers["Authorization"] = f"Bearer {self.token}"
                    response = requests.post(url, headers=headers, data=data)

            response.raise_for_status()
            result = response.json()

            if result.get("status") == "waiting":
                return {
                    "success": True,
                    "message_id": result.get("id"),
                    "status": result.get("status"),
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "SMS yuborishda xatolik"),
                }

        except requests.RequestException as e:
            logger.error(f"SMS yuborishda xatolik: {e}")
            return {"success": False, "error": str(e)}

    def get_sms_status(self, message_id: str) -> Dict[str, Any]:
        """SMS holatini tekshirish"""
        try:
            if not self.token:
                self.get_token()

            url = f"{self.base_url}/message/sms/status/{message_id}"
            headers = {"Authorization": f"Bearer {self.token}"}

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            logger.error(f"SMS holat tekshirishda xatolik: {e}")
            return {"success": False, "error": str(e)}


# Global SMS service instance
sms_service = EskizSMSService()


class SMSService:
    """SMS xizmati uchun wrapper klass"""

    @staticmethod
    def send_sms(phone: str, message: str) -> bool:
        """SMS yuborish (sodda interface)"""
        result = sms_service.send_sms(phone, message)
        return result.get("success", False)

    @staticmethod
    def send_verification_code(phone: str, code: str) -> bool:
        """Tasdiqlash kodini yuborish"""
        message = (
            f"Tasdiqlash kodi: {code}\nBu kod 5 daqiqa davomida amal qiladi."
        )
        return SMSService.send_sms(phone, message)

    @staticmethod
    def send_password_reset_code(phone: str, code: str) -> bool:
        """Parol tiklash kodini yuborish"""
        message = f"Parol tiklash kodi: {code}\nBu kod 5 daqiqa davomida amal qiladi."
        return SMSService.send_sms(phone, message)

    @staticmethod
    def send_order_notification(phone: str, order_number: str) -> bool:
        """Buyurtma haqida xabar yuborish"""
        message = f"Buyurtmangiz #{order_number} qabul qilindi. Tez orada siz bilan bog'lanamiz."
        return SMSService.send_sms(phone, message)


@shared_task
def send_sms_async(phone: str, message: str) -> Dict[str, Any]:
    """Asinxron SMS yuborish"""
    return sms_service.send_sms(phone, message)


@shared_task
def send_verification_code_async(phone: str, code: str) -> Dict[str, Any]:
    """Asinxron tasdiqlash kodi yuborish"""
    message = f"Tasdiqlash kodi: {code}\nBu kod 5 daqiqa davomida amal qiladi."
    return sms_service.send_sms(phone, message)


@shared_task
def send_password_reset_code_async(phone: str, code: str) -> Dict[str, Any]:
    """Asinxron parol tiklash kodi yuborish"""
    message = (
        f"Parol tiklash kodi: {code}\nBu kod 5 daqiqa davomida amal qiladi."
    )
    return sms_service.send_sms(phone, message)


@shared_task
def send_order_notification_async(
    phone: str, order_number: str
) -> Dict[str, Any]:
    """Asinxron buyurtma xabari yuborish"""
    message = f"Buyurtmangiz #{order_number} qabul qilindi. Tez orada siz bilan bog'lanamiz."
    return sms_service.send_sms(phone, message)
