from django.test import TestCase


class SmokeTests(TestCase):
    def test_home_page_loads(self):
        response = self.client.get("/")
        self.assertIn(response.status_code, (200, 302))

    def test_login_page_loads(self):
        response = self.client.get("/login/")
        self.assertEqual(response.status_code, 200)

    def test_protected_page_redirects_when_not_logged_in(self):
        protected_url = "/dashboard/"
        response = self.client.get(protected_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)
