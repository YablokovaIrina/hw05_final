from django.test import TestCase
from django.urls import reverse

from posts.urls import app_name

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
    [f'/posts/{POST_ID}/comment/', 'add_comment', [POST_ID]],
    ['/follow/', 'follow_index', []],
    [f'/profile/{USERNAME}/follow/', 'profile_follow', [USERNAME]],
    [f'/profile/{USERNAME}/unfollow/', 'profile_unfollow', [USERNAME]],
]


class TestRoutes(TestCase):
    def test_routes(self):
        for url, route, args in ROUTES:
            with self.subTest(url=url, route=route, args=args):
                self.assertEqual(
                    url, reverse(f'{app_name}:{route}', args=args))
