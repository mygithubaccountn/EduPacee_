from django.test import TestCase
from django.urls import reverse


class SmokeTests(TestCase):
    """
    Ultra-safe smoke tests to ensure the Django application
    starts correctly and basic request handling works.
    """

    def test_root_url_responds(self):
        """
        The root URL should respond without a 500 error.
        """
        try:
            response = self.client.get("/")
            # Accept any status code except 500 (server error)
            self.assertNotEqual(
                response.status_code,
                500,
                f"Root URL returned 500 Internal Server Error"
            )
        except Exception as e:
            self.fail(f"Root URL raised an exception: {str(e)}")

    def test_login_url_exists(self):
        """
        The login URL should exist and respond without a 500 error.
        """
        try:
            # Try to get the login URL - use reverse with namespace
            login_url = reverse('edupace_app:login')
            response = self.client.get(login_url)
            # Accept any status code except 500 (server error)
            self.assertNotEqual(
                response.status_code,
                500,
                f"Login URL {login_url} returned 500 Internal Server Error"
            )
        except Exception as e:
            self.fail(f"Login URL raised an exception: {str(e)}")

    def test_admin_login_page_loads(self):
        """
        Django admin login page should always be available.
        This is the safest authentication-related smoke test.
        """
        try:
            response = self.client.get("/admin/login/")
            # Admin should always return 200
            self.assertEqual(
                response.status_code,
                200,
                f"Admin login page returned status code {response.status_code}, expected 200"
            )
        except Exception as e:
            self.fail(f"Admin login page raised an exception: {str(e)}")
