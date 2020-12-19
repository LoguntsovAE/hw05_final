from django.contrib.auth import get_user_model
from django.db import models

from django.utils.translation import gettext_lazy as _


User = get_user_model()


class Group(models.Model):
    title = models.CharField('Заголовок группы', max_length=200)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        default='',
        editable=False,
        related_name='user_groups')
    slug = models.SlugField(
        'Адрес',
        max_length=20,
        unique=True)
    description = models.TextField('Описание')

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст в этом поле')
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts')
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        blank=True, null=True,
        verbose_name='Группа',
        help_text='Необязательно',
        related_name='posts')
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True, null=True)
    # post_like = models.ManyToManyField(
    #     User,
    #     related_name='post_liked',
    #     blank=True)

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments')
    text = models.TextField(
        'Текст комментария',
        help_text='Текст комментария')
    created = models.DateTimeField(
        'Дата комментария',
        auto_now_add=True)

    class Meta:
        ordering = ('-created',)


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['user', 'author'],
                name = 'unique_author_user_following',
            ),
        ]


class Like(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes')
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['post', 'user'],
                name = 'unique_user_post',
            ),
        ]

    def __str__(self):
        return f'User: {self.user} liked post: {self.post}' 