import shutil
import tempfile
from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Group, Post, Comment, User


USERNAME = 'UserAuthor'
NOT_AUTHOR = 'NotAuthor'
GROUP_TITLE = 'Группа1'
GROUP_SLUG = 'test_slug'
GROUP_DESCRIPTION = 'Тестовая группа 1'
GROUP_TITLE_NEW = 'Группа2'
GROUP_SLUG_NEW = 'test_slug_new'
GROUP_DESCRIPTION_NEW = 'Тестовая группа 2'
CREATE_POST_URL = reverse('posts:post_create')
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
LOGIN_URL = reverse('users:login')
POST_TEXT = 'Я все успею до жесткого дедлайна'
POST_TEXT_NEW = 'У меня получилось сдать все работы во время!'
POST_TEST_TEXT = 'Не автор не сможет поменять этот текст'
REDIRECT_URL = f'{LOGIN_URL}?next={CREATE_POST_URL}'
IMAGE = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
IMAGE_NAME = 'small.gif'
IMAGE_TYPE = 'image/gif'
UPLOAD_TO = 'posts/'
IMAGE_NAME_2 = 'sml.gif'

COMMENT_TEXT = 'Текст комментария'
COMMENT_TEXT_NEW = 'Новый текст комментария'


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.post_author = User.objects.create_user(
            username=USERNAME,
        )
        cls.not_author = User.objects.create_user(username=NOT_AUTHOR)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.group2 = Group.objects.create(
            title=GROUP_TITLE_NEW,
            slug=GROUP_SLUG_NEW,
            description=GROUP_DESCRIPTION_NEW,
        )
        cls.post = Post.objects.create(
            author=cls.post_author,
            text=POST_TEXT,
            group=cls.group,
        )
        cls.COMMENT_URL = reverse('posts:add_comment', args=[cls.post.id])
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.id])
        cls.COMMENT_REDIRECT_URL = f'{LOGIN_URL}?next={cls.COMMENT_URL}'
        cls.guest = Client()
        cls.author = Client()
        cls.author.force_login(cls.post_author)
        cls.notauthor = Client()
        cls.notauthor.force_login(cls.not_author)


    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def test_author_create_post(self):
        Post.objects.all().delete()
        image = SimpleUploadedFile(
            name=IMAGE_NAME,
            content=IMAGE,
            content_type=IMAGE_TYPE)
        form_data = {
            'text': POST_TEXT,
            'group': self.group.id,
            'image': image,
        }
        response = self.author.post(
            CREATE_POST_URL,
            data=form_data,
            follow=True
        )
        post = Post.objects.get()
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.post_author)
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(
            post.image.name,
            f"{UPLOAD_TO}{form_data['image']}"
        )
        self.assertRedirects(response, PROFILE_URL)

    def test_author_edit_post(self):
        image = SimpleUploadedFile(
            name=IMAGE_NAME_2,
            content=IMAGE,
            content_type=IMAGE_TYPE)
        form_data = {
            'text': POST_TEXT_NEW,
            'group': self.group2.id,
            'image': image,
        }
        response = self.author.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True
        )
        post = response.context.get('post')
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(
            post.image.name,
            f"{UPLOAD_TO}{form_data['image']}"
        )
        self.assertRedirects(response, self.POST_DETAIL_URL)


    def test_guest_create_post(self):
        Post.objects.all().delete()
        image = SimpleUploadedFile(
            name=IMAGE_NAME,
            content=IMAGE,
            content_type=IMAGE_TYPE)
        form_data = {
            'text': POST_TEXT,
            'group': self.group.id,
            'image': image
        }
        response = self.guest.post(
            CREATE_POST_URL,
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, REDIRECT_URL)
        self.assertEqual(Post.objects.count(), 0)

    def test_add_comments_show_correct_context(self):
        Comment.objects.all().delete()
        form_data = {
            'text': COMMENT_TEXT,
        }
        response = self.author.post(
            self.COMMENT_URL,
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.get()
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.author, self.post_author)
        self.assertEqual(comment.post, self.post)
        self.assertRedirects(response, self.POST_DETAIL_URL)

    def test_guest_create_comment(self):
        Comment.objects.all().delete()
        form_data = {
            'text': COMMENT_TEXT_NEW,
        }
        response = self.guest.post(
            self.COMMENT_URL,
            data=form_data
        )
        self.assertEqual(Comment.objects.count(), 0)
        self.assertRedirects(
            response,
            self.COMMENT_REDIRECT_URL
        )

    def test_not_author_edit_post(self):
        image = SimpleUploadedFile(
            name=IMAGE_NAME,
            content=IMAGE,
            content_type=IMAGE_TYPE)
        form_data = {
            'text': POST_TEST_TEXT,
            'group': self.group2.id,
            'image': image
        }
        clients = [self.guest, self.notauthor]
        for client in clients:
            with self.subTest(client=client):
                client.post(
                    self.POST_EDIT_URL,
                    data=form_data,
                    follow=True
                )
                edited_post = Post.objects.filter(id=self.post.id).get()
                self.assertEqual(self.post.text, edited_post.text)
                self.assertEqual(self.post.group, edited_post.group)
                self.assertEqual(self.post.author, edited_post.author)
                self.assertEqual(self.post.image, edited_post.image)
