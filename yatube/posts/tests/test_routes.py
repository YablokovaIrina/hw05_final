from django.test import TestCase
from django.urls import reverse

USERNAME = 'User'
SLUG = 'test_slug'
POST_ID = 1

ROUTES = [
    ['/', 'index', []],
    [f'/group/{SLUG}/', 'group_list', [SLUG]],
    ['/create/', 'post_create', []],
    [f'/profile/{USERNAME}/', 'profile', [USERNAME]],
    [f'/posts/{POST_ID}/', 'post_detail', [POST_ID]],
    [f'/posts/{POST_ID}/edit/', 'post_edit', [POST_ID]],
]


class TestRoutes(TestCase):
    def test_routes(self):
        for url, route, args in ROUTES:
            with self.subTest(url=url, route=route, args=args):
                self.assertEqual(url, reverse(f'posts:{route}', args=args))
