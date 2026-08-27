"""
Accounts Services

Owner: Mason
Responsibility: Business logic for authentication and user management

Service functions to implement:
# TODO: register_user(data)
#   - Validate registration data
#   - Create user account
#   - Create wallet (coordinate with Naomi)
#   - Hash password securely
#   - Return user object

# TODO: authenticate_user(email/phone, password)
#   - Find user by email or phone
#   - Verify password
#   - Generate JWT tokens
#   - Return tokens and user object

# TODO: update_profile(user, data)
#   - Update user fields
#   - Validate email/phone uniqueness
#   - Return updated user

# TODO: verify_password(user, password)
#   - Compare provided password with hash
#   - Return boolean

# TODO: generate_tokens(user)
#   - Create access token (1 hour)
#   - Create refresh token (7 days)
#   - Add user info to claims
#   - Return tokens dict
"""

from django.db import IntegrityError, transaction
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


def generate_tokens(user):
    """Create a JWT access/refresh pair for an authenticated account."""
    refresh = RefreshToken.for_user(user)
    refresh["role"] = user.role
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


def register_user(data):
    """Create an account safely; wallet creation remains owned by the wallet app."""
    try:
        with transaction.atomic():
            return User.objects.create_user(**data)
    except IntegrityError as error:
        # Serializers normally catch duplicates. This protects concurrent requests.
        raise ValueError("An account with that email or phone already exists.") from error


def authenticate_user(*, email=None, phone=None, password):
    """Authenticate against either unique identity without leaking account existence."""
    lookup = {"email__iexact": email} if email else {"phone": phone}
    user = User.objects.filter(**lookup).first()
    if not user or not user.is_active or not user.check_password(password):
        return None
    return user


def update_profile(user, data):
    """Persist only serializer-approved account fields."""
    for field, value in data.items():
        setattr(user, field, value)
    user.save(update_fields=[*data.keys(), "updated_at"])
    return user


def change_password(user, old_password, new_password):
    """Check the existing secret before changing and hashing the replacement."""
    if not user.check_password(old_password):
        return False
    user.set_password(new_password)
    user.save(update_fields=["password"])
    return True


def blacklist_refresh_token(refresh_token):
    """Invalidate a refresh token so it cannot obtain any more access tokens."""
    token = RefreshToken(refresh_token)
    token.blacklist()
