from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
CHARS = 20


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название группы')
    slug = models.SlugField(
        unique=True, max_length=50,
        verbose_name='Идентификатор'
    )
    description = models.TextField(verbose_name='Описание группы')

    class Meta:
        verbose_name_plural = 'Группы'
        verbose_name = 'Группу'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE, related_name="posts",
        verbose_name='Автор поста'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name="posts",
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:CHARS]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Напишите свой комментарий'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата комментария'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:CHARS]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписка',
    )
    PHRASE = f'{user} подписан на {author}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('user', 'author'),
                                    name='unique_follow'),
            models.CheckConstraint(
                check=~models.Q(user=models.F("author")),
                name='prevent self-following')
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        data = (
            self.user,
            self.author
        )
        return(self.PHRASE.format(user=data, author=data))
