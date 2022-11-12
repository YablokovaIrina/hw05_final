import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from yatube.settings import POSTS_ON_PAGE
from posts.models import Group, Post, Follow, User

GROUP_TITLE = 'Группа1'
GROUP_SLUG = 'test_slug'
GROUP_DESCRIPTION = 'Тестовая группа 1'
POST_TEXT = 'Тестовый текст'
USERNAME = 'Username'
FOLLOWER = 'Follower'
NOT_FOLLOWER = 'NotFollower'

INDEX_URL = reverse('posts:index')
GROUP_LIST_URL = reverse('posts:group_list', args=[GROUP_SLUG])
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
POSTS_ON_OTHER_PAGE = 3
SECOND_PAGE = '?page=2'

GROUP_TITLE_OTHER = 'Другая группа'
GROUP_SLUG_OTHER = 'test_slug_other'
GROUP_DESCRIPTION_OTHER = 'Тестовая группа 2'
GROUP_LIST_URL_OTHER = reverse('posts:group_list', args=[GROUP_SLUG_OTHER])

SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
UPLOADED = SimpleUploadedFile(
    name='small.gif',
    content=SMALL_GIF,
    content_type='image/gif'
)

FOLLOW_URL = reverse('posts:follow_index')
PROFILE_FOLLOW_URL = reverse(
    'posts:profile_follow',
    args=[USERNAME]
)
PROFILE_UNFOLLOW_URL = reverse(
    'posts:profile_unfollow',
    args=[USERNAME]
)

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.follower = User.objects.create_user(username=FOLLOWER)
        cls.not_follower = User.objects.create_user(username=NOT_FOLLOWER)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.group2 = Group.objects.create(
            title=GROUP_TITLE_OTHER,
            slug=GROUP_SLUG_OTHER,
            description=GROUP_DESCRIPTION_OTHER,
        )
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user,
            group=cls.group,
            image=UPLOADED,
        )
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.guest = Client()
        cls.author = Client()
        cls.author.force_login(cls.user)
        cls.follow = Client()
        cls.follow.force_login(cls.follower)
        cls.not_follow = Client()
        cls.not_follow.force_login(cls.not_follower)

    def setUp(self):
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def check_post_info(self, post):
        with self.subTest(post=post):
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.group.id, self.post.group.id)
            self.assertEqual(post.id, self.post.id)
            self.assertEqual(post.image, self.post.image)

    def test_show_correct_contex(self):
        Follow.objects.create(user=self.follower, author=self.user)
        urls = [
            INDEX_URL,
            GROUP_LIST_URL,
            PROFILE_URL,
            self.POST_DETAIL_URL,
            FOLLOW_URL,
        ]
        for url in urls:
            response = self.follow.get(url)
            if 'page_obj' not in response.context:
                post = response.context['post']
            else:
                self.assertEqual(len(response.context['page_obj']), 1)
                post = response.context['page_obj'][0]
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.group.id, self.post.group.id)
            self.assertEqual(post.id, self.post.id)
            self.assertEqual(post.image, self.post.image)

    def test_groups_page_show_correct_context(self):
        group = self.author.get(GROUP_LIST_URL).context['group']
        self.assertEqual(self.group.id, group.id)
        self.assertEqual(self.group.title, group.title)
        self.assertEqual(self.group.slug, group.slug)
        self.assertEqual(self.group.description, group.description)

    def test_profile_page_show_correct_context(self):
        response = self.author.get(
            PROFILE_URL
        )
        self.assertEqual(response.context['author'], self.user)

    def test_detail_page_show_correct_context(self):
        response = self.author.get(
            self.POST_DETAIL_URL
        )
        self.check_post_info(response.context['post'])

    def test_post_is_not_in_group_and_feed(self):
        urls = [
            FOLLOW_URL,
            GROUP_LIST_URL_OTHER
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.author.get(url)
                self.assertNotIn(self.post, response.context['page_obj'])

    def test_paginator_on_pages(self):
        Post.objects.all().delete()
        Post.objects.bulk_create(
            Post(
                text=f'Post {i}',
                author=self.user,
                group=self.group,
                image=UPLOADED
            )
            for i in range(POSTS_ON_PAGE + POSTS_ON_OTHER_PAGE)
        )
        pages_and_records = {
            INDEX_URL: POSTS_ON_PAGE,
            INDEX_URL + SECOND_PAGE: POSTS_ON_OTHER_PAGE,
            GROUP_LIST_URL: POSTS_ON_PAGE,
            GROUP_LIST_URL + SECOND_PAGE: POSTS_ON_OTHER_PAGE,
            PROFILE_URL: POSTS_ON_PAGE,
            PROFILE_URL + SECOND_PAGE: POSTS_ON_OTHER_PAGE,
        }
        for page, records in pages_and_records.items():
            with self.subTest(page=page):
                response = self.guest.get(page)
                self.assertEqual(len(response.context['page_obj']), records)

    def test_cache_index(self):
        response1 = self.author.get(INDEX_URL)
        Post.objects.all().delete()
        response2 = self.author.get(INDEX_URL)
        cache.clear()
        response3 = self.author.get(INDEX_URL)
        self.assertEqual(response2.content, response1.content)
        self.assertNotEqual(response3.content, response2.content)

    def test_follow(self): 
        Follow.objects.all().delete()
        self.assertTrue(Follow.objects.filter(
            user=self.follower,
            author=self.user
        ), self.follow.get(PROFILE_FOLLOW_URL))
        
    def test_unfollow(self):
        self.assertFalse(Follow.objects.filter(
            user=self.follower,
            author=self.user).exists())
