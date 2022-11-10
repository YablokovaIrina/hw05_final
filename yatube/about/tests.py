from django.test import TestCase, Client


class StaticURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_pages_urls_exist_at_desired_location_about(self):
        urls = [
            '/about/author/',
            '/about/tech/'
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_urls_use_correct_templates_about(self):
        templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
