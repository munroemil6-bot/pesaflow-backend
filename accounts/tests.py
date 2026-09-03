
from rest_framework import status
from rest_framework.test import APITestCase

from .models import User


class AuthenticationEndpointTests(APITestCase):
    """Keep Mason's public authentication contract safe during team integration."""

    register_url = "/api/accounts/register/"
    login_url = "/api/accounts/login/"

    def payload(self, **overrides):
        data = {
            "full_name": "Mason Developer",
            "email": "mason@example.com",
            "phone": "0712345678",
            "password": "PesaFlow!StrongPassword2026",
        }
        data.update(overrides)
        return data

    def register_and_login(self):
        self.client.post(self.register_url, self.payload(), format="json")
        response = self.client.post(
            self.login_url,
            {"email": "mason@example.com", "password": "PesaFlow!StrongPassword2026"},
            format="json",
        )
        return response.data

    def test_register_creates_user_without_exposing_password(self):
        response = self.client.post(self.register_url, self.payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"]["email"], "mason@example.com")
        self.assertNotIn("password", response.data["user"])
        self.assertTrue(User.objects.get(email="mason@example.com").check_password(self.payload()["password"]))

    def test_login_profile_and_profile_update(self):
        tokens = self.register_and_login()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        response = self.client.get("/api/accounts/profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.put(
            "/api/accounts/profile/", {"full_name": "Updated Mason"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["full_name"], "Updated Mason")

    def test_login_by_phone_and_reject_invalid_credentials(self):
        self.client.post(self.register_url, self.payload(), format="json")
        response = self.client.post(
            self.login_url,
            {"phone": "0712345678", "password": "PesaFlow!StrongPassword2026"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            self.login_url,
            {"email": "mason@example.com", "password": "not-the-password"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_deactivated_account_cannot_login_until_reactivated(self):
        self.client.post(self.register_url, self.payload(), format="json")
        user = User.objects.get(email="mason@example.com")
        user.is_active = False
        user.save(update_fields=["is_active"])

        response = self.client.post(
            self.login_url,
            {"email": "mason@example.com", "password": "PesaFlow!StrongPassword2026"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "Your account has been deactivated. Please contact the admin on 0723274962.",
        )

        user.is_active = True
        user.save(update_fields=["is_active"])
        response = self.client.post(
            self.login_url,
            {"email": "mason@example.com", "password": "PesaFlow!StrongPassword2026"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_public_auth_endpoints_ignore_a_stale_authorization_header(self):
        """An old browser token must not prevent a person from logging in again."""
        self.client.credentials(HTTP_AUTHORIZATION="Bearer expired-or-invalid-token")

        response = self.client.post(self.register_url, self.payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(
            self.login_url,
            {"email": "mason@example.com", "password": "PesaFlow!StrongPassword2026"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

        response = self.client.post("/api/accounts/refresh/", {"refresh": "invalid"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_logout_and_change_password(self):
        tokens = self.register_and_login()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        response = self.client.post("/api/accounts/refresh/", {"refresh": tokens["refresh"]}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

        response = self.client.post(
            "/api/accounts/change-password/",
            {"old_password": "PesaFlow!StrongPassword2026", "new_password": "New!StrongPassword2026"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post("/api/accounts/logout/", {"refresh": tokens["refresh"]}, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
