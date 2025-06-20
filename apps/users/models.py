import random
import string

from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.common.models import BaseModel


class User(AbstractUser, BaseModel):
    username = None
    phone = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    default_shipping_address = models.TextField(blank=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone


class VerificationCode(BaseModel):
    phone = models.CharField(max_length=20)
    code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.phone} - {self.code}"

    @classmethod
    def generate_code(cls):
        return "".join(random.choices(string.digits, k=6))
