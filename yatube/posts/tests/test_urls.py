from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group, User

USERNAME = 'UserAuthor'
USERNAME_2 = 'User'
GROUP_TITLE = 'Группа1'
GROUP_SLUG = 'test_slug'
GROUP_DESCRIPTION = 'Тестовая группа 1'
POST_TEXT = 'Я все успею до жесткого дедлайна'

INDEX_URL = reverse('posts:index')
POST_CREATE_URL = reverse('posts:post_create')
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
GROUP_LIST_URL = reverse('posts:group_list', args=[GROUP_SLUG])
LOGIN_URL = reverse('users:login')
FOLLOW_INDEX_URL = reverse('posts:follow_index')
PROFILE_FOLLOW_URL = reverse(
    'posts:profile_follow', args=[USERNAME])
PROFILE_UNFOLLOW_URL = reverse(
    'posts:profile_unfollow', args=[USERNAME])

POST_CREATE_REDIRECT = f'{LOGIN_URL}?next={POST_CREATE_URL}'
FOLLOW_REDIRECT = f'{LOGIN_URL}?next={FOLLOW_INDEX_URL}'
PROFILE_FOLLOW_REDIRECT = f'{LOGIN_URL}?next={PROFILE_FOLLOW_URL}'
PROFILE_UNFOLLOW_REDIRECT = f'{LOGIN_URL}?next={PROFILE_UNFOLLOW_URL}'


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.user2 = User.objects.create_user(username=USERNAME_2)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user,
            group=cls.group,
        )
        cls.POST_DETAIL_URL = reverse(
            'posts:post_detail', kwargs={'post_id': cls.post.id}
        )
        cls.POST_EDIT_URL = reverse(
            'posts:post_edit', kwargs={'post_id': cls.post.id}
        )
        cls.POST_EDIT_REDIRECT = f'{LOGIN_URL}?next={cls.POST_EDIT_URL}'
        cls.guest = Client()
        cls.another = Client()
        cls.another.force_login(cls.user2)
        cls.author = Client()
        cls.author.force_login(cls.user)

    def setUp(self):
        cache.clear()

    def test_pages_urls_at_desired_location_posts_for_users(self):
        urls_names = [
            [INDEX_URL, self.guest, 200],
            [GROUP_LIST_URL, self.guest, 200],
            [self.POST_DETAIL_URL, self.guest, 200],
            [POST_CREATE_URL, self.guest, 302],
            [self.POST_EDIT_URL, self.guest, 302],
            [PROFILE_URL, self.another, 200],
            [POST_CREATE_URL, self.another, 200],
            [self.POST_EDIT_URL, self.another, 302],
            [self.POST_EDIT_URL, self.author, 200],
            ['/unexisting_page/', self.guest, 404],
            [FOLLOW_INDEX_URL, self.another, 200],
            [FOLLOW_INDEX_URL, self.guest, 302],
            [PROFILE_FOLLOW_URL, self.another, 302],
            [PROFILE_FOLLOW_URL, self.guest, 302],
            [PROFILE_FOLLOW_URL, self.author, 302],
            [PROFILE_UNFOLLOW_URL, self.another, 302],
            [PROFILE_UNFOLLOW_URL, self.guest, 302],
            [PROFILE_UNFOLLOW_URL, self.author, 404],
        ]
        for url, client, code in urls_names:
            with self.subTest(url=url, client=client, code=code):
                self.assertEqual(client.get(url).status_code, code)

    def test_urls_redirects_posts(self):
        urls_redirect = [
            [POST_CREATE_URL, self.guest, POST_CREATE_REDIRECT],
            [self.POST_EDIT_URL, self.guest, self.POST_EDIT_REDIRECT],
            [self.POST_EDIT_URL, self.another, self.POST_DETAIL_URL],
            [FOLLOW_INDEX_URL, self.guest, FOLLOW_REDIRECT],
            [PROFILE_FOLLOW_URL, self.guest, PROFILE_FOLLOW_REDIRECT],
            [PROFILE_UNFOLLOW_URL, self.guest, PROFILE_UNFOLLOW_REDIRECT],
            [PROFILE_FOLLOW_URL, self.author, PROFILE_URL],
            [PROFILE_FOLLOW_URL, self.another, PROFILE_URL],
            [PROFILE_UNFOLLOW_URL, self.another, PROFILE_URL],
        ]
        for url, client, redirect in urls_redirect:
            with self.subTest(url=url, client=client, redirect=redirect):
                self.assertRedirects(client.get(url), redirect)

    def test_urls_uses_correct_templates(self):
        template_url_names = [
            [INDEX_URL, self.guest, 'posts/index.html'],
            [PROFILE_URL, self.guest, 'posts/profile.html'],
            [self.POST_DETAIL_URL, self.guest, 'posts/post_detail.html'],
            [POST_CREATE_URL, self.author, 'posts/create_post.html'],
            [GROUP_LIST_URL, self.author, 'posts/group_list.html'],
            [self.POST_EDIT_URL, self.author, 'posts/create_post.html'],
            [FOLLOW_INDEX_URL, self.author, 'posts/follow.html'],
        ]
        for url, client, template in template_url_names:
            with self.subTest(url=url, client=client, template=template):
                self.assertTemplateUsed(client.get(url), template)
