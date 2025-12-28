from django.test import TestCase
from django.conf import settings
from django.urls import reverse, NoReverseMatch


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
        # Accept any valid HTTP response (200, 302 redirect, 403 forbidden, etc.)
        self.assertIn(
            response.status_code,
            [200, 301, 302, 303, 307, 308, 403, 404],
            f"Root URL returned unexpected status code: {response.status_code}"
        )

    def test_login_url_exists(self):
        """
        The configured LOGIN_URL should exist and respond.
        """
        login_url_setting = getattr(settings, "LOGIN_URL", "/accounts/login/")
        
        # Try to resolve named URL first
        try:
            login_url = reverse(login_url_setting)
        except (NoReverseMatch, Exception):
            # If reverse fails, try using it as a direct path
            # Remove namespace if present (e.g., 'edupace_app:login' -> 'login')
            if ':' in login_url_setting:
                url_name = login_url_setting.split(':')[-1]
                try:
                    login_url = reverse(url_name)
                except (NoReverseMatch, Exception):
                    # Fallback to direct path
                    login_url = "/login/"
            else:
                login_url = login_url_setting
        
        response = self.client.get(login_url)
        # Accept 200 (success) or 302 (redirect) as valid responses
        self.assertIn(
            response.status_code,
            [200, 301, 302, 303, 307, 308],
            f"Login URL {login_url} returned unexpected status code: {response.status_code}"
        )

    def test_admin_login_page_loads(self):
        """
        Django admin login page should always be available.
        This is the safest authentication-related smoke test.
        """
        response = self.client.get("/admin/login/")
        self.assertEqual(
            response.status_code,
            200,
            f"Admin login page returned status code {response.status_code}, expected 200"
        )
