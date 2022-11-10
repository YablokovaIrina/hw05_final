from django.test import TestCase, Client


class PostURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_signup_url_exists_at_desired_location(self):
        """Страница /auth/signup/ доступна всем пользователям."""
        response = self.guest_client.get("/auth/signup/")
        self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            "/auth/signup/": "users/signup.html",
        }
        for url, template in templates_url_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
