from datetime import timedelta

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers

from apps.common.utils.sms_mailing import (
    send_verification_code_async,
)

from .models import User, VerificationCode


class AuthorizeSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True, required=False)

    def validate_phone(self, value):
        if not value.startswith("+"):
            raise serializers.ValidationError("Phone number must start with +")
        return value

    def create(self, validated_data):
        phone = validated_data["phone"]
        code = VerificationCode.generate_code()
        expires_at = timezone.now() + timedelta(minutes=5)

        # Delete old codes for this phone
        VerificationCode.objects.filter(phone=phone).delete()

        # Create new verification code
        verification_code = VerificationCode.objects.create(
            phone=phone, code=code, expires_at=expires_at
        )

        # Send SMS via Eskiz
        send_verification_code_async.delay(phone, code)

        return verification_code


class VerifySerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=6)
    password = serializers.CharField(write_only=True, required=False)
    name = serializers.CharField(max_length=255, required=False)

    def validate(self, attrs):
        phone = attrs["phone"]
        code = attrs["code"]

        try:
            verification_code = VerificationCode.objects.get(
                phone=phone,
                code=code,
                is_used=False,
                expires_at__gt=timezone.now(),
            )
        except VerificationCode.DoesNotExist:
            raise serializers.ValidationError(
                "Invalid or expired verification code"
            )

        attrs["verification_code"] = verification_code
        return attrs

    def create(self, validated_data):
        phone = validated_data["phone"]
        password = validated_data.get("password")
        name = validated_data.get("name", "")
        verification_code = validated_data["verification_code"]

        # Mark verification code as used
        verification_code.is_used = True
        verification_code.save()

        # Check if user exists
        user, created = User.objects.get_or_create(
            phone=phone, defaults={"name": name}
        )

        # If password provided and user is new, set password
        if password and created:
            validate_password(password)
            user.set_password(password)
            user.save()

        return user


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        phone = attrs["phone"]
        password = attrs["password"]

        user = authenticate(username=phone, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials")

        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "phone",
            "name",
            "email",
            "default_shipping_address",
            "date_joined",
        ]
        read_only_fields = ["id", "phone", "date_joined"]


class ForgotPasswordSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)

    def validate_phone(self, value):
        try:
            User.objects.get(phone=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "User with this phone number does not exist"
            )
        return value


class ResetPasswordSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        phone = attrs["phone"]
        code = attrs["code"]

        try:
            verification_code = VerificationCode.objects.get(
                phone=phone,
                code=code,
                is_used=False,
                expires_at__gt=timezone.now(),
            )
        except VerificationCode.DoesNotExist:
            raise serializers.ValidationError(
                "Invalid or expired verification code"
            )

        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")

        attrs["verification_code"] = verification_code
        attrs["user"] = user
        return attrs
