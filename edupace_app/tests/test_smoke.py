from django.test import TestCase
from django.conf import settings
from django.urls import reverse


class SmokeTests(TestCase):
    """
    Ultra-safe smoke tests to ensure the Django application
    starts correctly and basic request handling works.
    """

    def test_root_url_responds(self):
        """
        The root URL should respond with a valid HTTP status.
        """
        response = self.client.get("/")
        self.assertTrue(
            response.status_code in (200, 302, 403),
            f"Unexpected status code: {response.status_code}"
        )

    def test_login_url_exists(self):
        """
        The configured LOGIN_URL should exist and respond.
        """
        login_url_setting = getattr(settings, "LOGIN_URL", "/accounts/login/")
        # If LOGIN_URL is a named URL, resolve it; otherwise use as-is
        try:
            login_url = reverse(login_url_setting)
        except Exception:
            # If reverse fails, assume it's a direct path
            login_url = login_url_setting
        
        response = self.client.get(login_url)
        self.assertTrue(
            response.status_code in (200, 302),
            f"Login URL {login_url} returned {response.status_code}"
        )

    def test_admin_login_page_loads(self):
        """
        Django admin login page should always be available.
        This is the safest authentication-related smoke test.
        """
        response = self.client.get("/admin/login/")
        self.assertEqual(response.status_code, 200)
