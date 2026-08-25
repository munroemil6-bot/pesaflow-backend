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

# TODO: @api_view(['POST']) registration view
# TODO: @api_view(['POST']) login view
# TODO: @api_view(['POST']) token refresh view
# TODO: @api_view(['GET', 'PUT']) profile view
# TODO: @api_view(['POST']) logout view
# TODO: @api_view(['POST']) change password view
