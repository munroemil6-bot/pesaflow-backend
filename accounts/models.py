"""User and authentication models for PesaFlow.

Owner: Mason
"""

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """Create users with normalized email addresses and safe admin defaults."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a user using email as the login identifier."""
        if not email:
            raise ValueError("The email address is required.")

        email = self.normalize_email(email).strip().lower()
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Create and save an administrator with all required privileges."""
        if not password:
            raise ValueError("A password is required for a superuser.")

        extra_fields.setdefault("role", User.Role.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("A superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("A superuser must have is_superuser=True.")
        if extra_fields.get("role") != User.Role.ADMIN:
            raise ValueError("A superuser must have role='admin'.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """A PesaFlow account authenticated by email address."""

    class Role(models.TextChoices):
        USER = "user", "User"
        ADMIN = "admin", "Admin"

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=120)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone", "full_name"]

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["role", "is_active"])]

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        """Persist a consistently normalized email address."""
        if self.email:
            self.email = self.__class__.objects.normalize_email(self.email).strip().lower()
        super().save(*args, **kwargs)

    def get_full_name(self):
        """Return the user's display name for Django integrations."""
        return self.full_name

    def get_short_name(self):
        """Return the first component of the user's display name."""
        return self.full_name.split(maxsplit=1)[0] if self.full_name else ""

    def verify_password(self, password):
        """Return whether the supplied password matches this account."""
        return self.check_password(password)

    def to_dict(self):
        """Return public profile data without password or permission internals."""
        return {
            "id": self.pk,
            "email": self.email,
            "phone": self.phone,
            "full_name": self.full_name,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
