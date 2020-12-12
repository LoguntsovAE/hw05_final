from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.deletion import CASCADE
from pytils.translit import slugify

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=20, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:20]
        super().save(*args, **kwargs)


class Post(models.Model):
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст в этом поле'
        )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
        )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author_posts'
        )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        blank=True, null=True,
        verbose_name='Группа',
        help_text='Необязательно',
        related_name='group_posts'
        )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True, null=True)

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
        )
    author = models.ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='comments'
        )
    text = models.TextField(
        'Текст комментария',
        help_text='Текст комментария'
        )
    created = models.DateTimeField(
        'Дата комментария',
        auto_now_add=True
        )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='follower',
        )
    author = models.ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='following'
        )
