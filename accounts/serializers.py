
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Public account fields. Passwords and permission internals stay private."""

    class Meta:
        model = User
        fields = ("id", "email", "phone", "full_name", "role", "created_at", "updated_at")
        read_only_fields = ("id", "role", "created_at", "updated_at")


class RegisterSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=120)
    email = serializers.EmailField(max_length=254)
    phone = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)

    def validate_full_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Full name cannot be blank.")
        return value

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def validate_phone(self, value):
        value = value.strip()
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("An account with this phone already exists.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, max_length=254)
    phone = serializers.CharField(required=False, max_length=20)
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        if bool(attrs.get("email")) == bool(attrs.get("phone")):
            raise serializers.ValidationError("Provide exactly one of email or phone.")
        if attrs.get("email"):
            attrs["email"] = attrs["email"].strip().lower()
        if attrs.get("phone"):
            attrs["phone"] = attrs["phone"].strip()
        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    """Only identity details may be changed through the profile endpoint."""

    class Meta:
        model = User
        fields = ("full_name", "email", "phone")

    def validate_full_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Full name cannot be blank.")
        return value

    def validate_email(self, value):
        value = value.strip().lower()
        user = self.instance
        if User.objects.filter(email__iexact=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def validate_phone(self, value):
        value = value.strip()
        user = self.instance
        if User.objects.filter(phone=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("An account with this phone already exists.")
        return value


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, trim_whitespace=False)
    new_password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)

    def validate_new_password(self, value):
        validate_password(value, self.context["request"].user)
        return value
