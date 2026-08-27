"""
Accounts Views

Owner: Mason
Responsibility: API endpoints for authentication and user management

API Endpoints to implement:
# TODO: POST /api/accounts/register/
#   - Accepts: full_name, email, phone, password
#   - Returns: user object + wallet creation
#   - Status: 201 CREATED or 400 BAD REQUEST

# TODO: POST /api/accounts/login/
#   - Accepts: email or phone, password
#   - Returns: access_token, refresh_token, user object
#   - Status: 200 OK or 401 UNAUTHORIZED

# TODO: POST /api/accounts/refresh/
#   - Accepts: refresh_token
#   - Returns: new access_token
#   - Status: 200 OK or 401 UNAUTHORIZED

# TODO: GET /api/accounts/profile/
#   - Returns: current user profile
#   - Status: 200 OK or 401 UNAUTHORIZED

# TODO: PUT /api/accounts/profile/
#   - Accepts: full_name, email, phone (any combination)
#   - Returns: updated user profile
#   - Status: 200 OK or 400 BAD REQUEST

# TODO: POST /api/accounts/logout/
#   - Invalidates refresh token
#   - Status: 204 NO CONTENT

# TODO: POST /api/accounts/change-password/
#   - Accepts: old_password, new_password
#   - Returns: success message
#   - Status: 200 OK or 400 BAD REQUEST
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    ProfileSerializer,
    RegisterSerializer,
    UserSerializer,
)
from .services import (
    authenticate_user,
    blacklist_refresh_token,
    change_password as change_user_password,
    generate_tokens,
    register_user,
    update_profile,
)


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = register_user(serializer.validated_data)
    return Response({"user": UserSerializer(user).data}, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([AllowAny])
def api_index(request):
    """List the public account API entry points for local developers."""
    return Response(
        {
            "service": "pesaflow-accounts",
            "endpoints": {
                "register": "POST /api/accounts/register/",
                "login": "POST /api/accounts/login/",
                "refresh": "POST /api/accounts/refresh/",
                "profile": "GET or PUT /api/accounts/profile/",
                "logout": "POST /api/accounts/logout/",
                "change_password": "POST /api/accounts/change-password/",
            },
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = authenticate_user(**serializer.validated_data)
    if not user:
        return Response(
            {"detail": "Invalid email/phone or password."}, status=status.HTTP_401_UNAUTHORIZED
        )
    return Response({**generate_tokens(user), "user": UserSerializer(user).data})


class RefreshTokenView(TokenRefreshView):
    """Public endpoint that exchanges a valid refresh token for an access token."""

    permission_classes = [AllowAny]


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def profile(request):
    if request.method == "GET":
        return Response({"user": UserSerializer(request.user).data})

    serializer = ProfileSerializer(request.user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    if not serializer.validated_data:
        return Response(
            {"detail": "Provide at least one profile field."}, status=status.HTTP_400_BAD_REQUEST
        )
    user = update_profile(request.user, serializer.validated_data)
    return Response({"user": UserSerializer(user).data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    refresh_token = request.data.get("refresh")
    if not refresh_token:
        return Response({"refresh": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)
    try:
        blacklist_refresh_token(refresh_token)
    except TokenError:
        return Response({"refresh": ["Invalid or expired token."]}, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    if not change_user_password(request.user, **serializer.validated_data):
        return Response(
            {"old_password": ["Current password is incorrect."]},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return Response({"detail": "Password changed successfully."})
