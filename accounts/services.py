

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
