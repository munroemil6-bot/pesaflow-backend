"""
Accounts Tests

Owner: Mason
Responsibility: Unit tests for authentication endpoints

Tests to implement:
# TODO: TestUserRegistration
#   - test_register_success
#   - test_register_invalid_email
#   - test_register_weak_password
#   - test_register_duplicate_email
#   - test_register_duplicate_phone

# TODO: TestUserLogin
#   - test_login_with_email
#   - test_login_with_phone
#   - test_login_invalid_credentials
#   - test_login_inactive_user
#   - test_login_missing_fields

# TODO: TestProfileEndpoints
#   - test_get_profile_authenticated
#   - test_get_profile_unauthenticated
#   - test_update_profile_success
#   - test_update_profile_invalid_data
#   - test_change_password_success

# TODO: TestTokenRefresh
#   - test_refresh_token_success
#   - test_refresh_token_expired
#   - test_refresh_token_invalid
"""

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
