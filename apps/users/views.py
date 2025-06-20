from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.common.responses import APIResponse
from apps.common.utils.sms_mailing import send_password_reset_code_async

from .models import VerificationCode
from .serializers import (
    AuthorizeSerializer,
    ForgotPasswordSerializer,
    LoginSerializer,
    ResetPasswordSerializer,
    UserSerializer,
    VerifySerializer,
)


@api_view(["POST"])
@permission_classes([AllowAny])
def authorize(request):
    """Request SMS verification code"""
    serializer = AuthorizeSerializer(data=request.data)
    if serializer.is_valid():
        verification_code = serializer.save()
        return APIResponse.success(
            message=f"Verification code sent to {verification_code.phone}"
        )
    return APIResponse.error("Invalid request", details=serializer.errors)


@api_view(["POST"])
@permission_classes([AllowAny])
def verify(request):
    """Verify SMS code and register/login user"""
    serializer = VerifySerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return APIResponse.success(
            {
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "expires_in": 3600,
            }
        )
    return APIResponse.error(
        "Invalid verification code", details=serializer.errors
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """Login with phone and password"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return APIResponse.success(
            {
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "expires_in": 3600,
            }
        )
    return APIResponse.error(
        "Invalid credentials",
        details=serializer.errors,
        status_code=status.HTTP_401_UNAUTHORIZED,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    """Logout and blacklist refresh token"""
    try:
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return APIResponse.error("Refresh token is required")

        token = RefreshToken(refresh_token)
        token.blacklist()
        return APIResponse.success(message="Successfully logged out")
    except TokenError:
        return APIResponse.error("Invalid token")


@api_view(["POST"])
@permission_classes([AllowAny])
def refresh_token(request):
    """Refresh access token"""
    try:
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return APIResponse.error("Refresh token is required")

        token = RefreshToken(refresh_token)
        return APIResponse.success(
            {"access_token": str(token.access_token), "expires_in": 3600}
        )
    except TokenError:
        return APIResponse.error(
            "Invalid refresh token", status_code=status.HTTP_401_UNAUTHORIZED
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def forgot_password(request):
    """Request password reset SMS"""
    serializer = ForgotPasswordSerializer(data=request.data)
    if serializer.is_valid():
        phone = serializer.validated_data["phone"]
        code = VerificationCode.generate_code()
        expires_at = timezone.now() + timedelta(minutes=5)

        # Delete old codes for this phone
        VerificationCode.objects.filter(phone=phone).delete()

        # Create new verification code
        VerificationCode.objects.create(
            phone=phone, code=code, expires_at=expires_at
        )

        # Send SMS
        send_password_reset_code_async.delay(phone, code)

        return APIResponse.success(
            message=f"Password reset code sent to {phone}"
        )
    return APIResponse.error(
        "User not found",
        details=serializer.errors,
        status_code=status.HTTP_404_NOT_FOUND,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password(request):
    """Reset password after verification"""
    serializer = ResetPasswordSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data["user"]
        verification_code = serializer.validated_data["verification_code"]
        new_password = serializer.validated_data["new_password"]

        # Mark verification code as used
        verification_code.is_used = True
        verification_code.save()

        # Update user password
        user.set_password(new_password)
        user.save()

        return APIResponse.success(message="Password reset successful")
    return APIResponse.error(
        "Invalid verification code", details=serializer.errors
    )


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def profile(request):
    """Get or update user profile"""
    if request.method == "GET":
        serializer = UserSerializer(request.user)
        return APIResponse.success(serializer.data)

    elif request.method == "PUT":
        serializer = UserSerializer(
            request.user, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return APIResponse.success(serializer.data)
        return APIResponse.error("Invalid request", details=serializer.errors)
