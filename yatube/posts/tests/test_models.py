from django.test import TestCase

from ..models import Group, Post, Comment, Follow, CHARS, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user2 = User.objects.create_user(username='user2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            text='Тестовый коммент',
            post=cls.post,
            author=cls.user,
        )
        cls.follow = Follow.objects.create(
            user=cls.user2,
            author=cls.user,
        )

    def test_models_have_correct_object_names(self):
        self.assertEqual(self.post.text[:CHARS], str(self.post))
        self.assertEqual(self.group.title, str(self.group))
        self.assertEqual(self.comment.text[:CHARS], str(self.comment))
        self.assertEqual(self.follow.PHRASE, str(self.follow))
