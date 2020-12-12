import tempfile

from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse

from posts.models import Comment, Follow, Post
from posts.settings import POSTS_PER_PAGE
from posts.tests.test_settings import TestSettings


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class PostPagesTests(TestSettings):

    def test_view_function_uses_correct_template(self):
        """ Тест для проверки того,
        что view функция использует верный шаблон"""
        TEMPLATE_NAMES = {
            'index.html': self.URL_NAMES['INDEX'],
            'posts/group.html': self.URL_NAMES['GROUP'],
            'posts/new.html': self.URL_NAMES['NEW_POST'],
            'posts/post_edit.html': self.URL_NAMES['POST_EDIT'],
            'posts/profile.html': self.URL_NAMES['PROFILE'],
            'posts/post.html': self.URL_NAMES['POST'],
        }
        for template, reverse_name in TEMPLATE_NAMES.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                if template == 'posts/post_edit.html':
                    template = 'posts/new.html'
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """ Тест проверяет контекст главной страницы"""
        response = self.authorized_client.get(self.URL_NAMES['INDEX'])
        self.assertIn('page', response.context)
        self.assertEqual(
            response.context['paginator'].page(1).object_list.count(),
            POSTS_PER_PAGE
            )

    def test_group_page_show_correct_context(self):
        """ Тест проверяет контекст страницы группы"""
        response = self.authorized_client.get(self.URL_NAMES['GROUP'])
        self.assertIn('page', response.context)
        self.assertEqual(response.context['group'], self.group)
        self.assertEqual(
            response.context["paginator"].page(1).object_list.count(),
            POSTS_PER_PAGE
            )

    def test_post_edit_show_correct_context(self):
        """ Тест проверяет контекст страницы редактирования поста"""
        response = self.authorized_client.get(self.URL_NAMES['POST_EDIT'])
        self.assertIn('form', response.context)
        self.assertEqual(response.context["post"], self.post)

    def test_profile_page_show_correct_context(self):
        """ Тест проверяет контекст страницы профиля"""
        response = self.authorized_client.get(self.URL_NAMES['PROFILE'])
        self.assertEqual(response.context["page"][0].author, self.user)
        self.assertIn('page', response.context)
        self.assertIn('profile', response.context)
        self.assertIn('paginator', response.context)
        posts_count = response.context['paginator'].page(2).object_list.count()
        self.assertEqual(posts_count, 2)

    def test_post_page_show_correct_context(self):
        """ Тест проверяет контекст страницы поста"""
        response = self.authorized_client.get(self.URL_NAMES['POST'])
        self.assertIn('post', response.context)
        self.assertIn('author', response.context)
        response_post = response.context['post']
        post_in_bd = Post.objects.get(
            author__username=self.user.username,
            id=self.post.id
            )
        self.assertEqual(response_post.text, post_in_bd.text)
        self.assertEqual(response_post.author, post_in_bd.author)
        if self.group:
            self.assertEqual(response_post.group, post_in_bd.group)
        if response_post.image:
            self.assertEqual(response_post.image, self.post.image)

    def test_page_context_include_image(self):
        """ Тестирование контекста страницы на наличие картинки """
        small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                b'\x01\x00\x80\x00\x00\x00\x00\x00'
                b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                b'\x0A\x00\x3B'
            )
        uploaded = SimpleUploadedFile(
            name='Тестовая картинка',
            content=small_gif,
            content_type='image/gif'
        )
        Post.objects.all().delete()
        post_with_image = Post.objects.create(
            id=1,
            text='Post text',
            author=self.user,
            group=self.group,
            image=uploaded,
            )
        client = self.authorized_client
        responses = {
            'index': client.get(self.URL_NAMES['INDEX']),
            'profile': client.get(self.URL_NAMES['PROFILE']),
            'group': client.get(self.URL_NAMES['GROUP']),
            'post': client.get(self.URL_NAMES['POST']),
        }
        for name, response in responses.items():
            with self.subTest(name=name):
                if name == 'post':
                    context = response.context.get('post').image
                else:
                    context = response.context.get('page').object_list[0].image
                self.assertEqual(post_with_image.image, context, name)

    def test_cache_index_page(self):
        response_1 = self.authorized_client.get(self.URL_NAMES['INDEX'])
        """Тестирование кэша главной страницы"""
        Post.objects.create(
            text='Кэш это круто',
            author=self.user,
        )
        response_2 = self.authorized_client.get(self.URL_NAMES['INDEX'])
        self.assertEqual(response_1.content, response_2.content)
        cache.clear()
        response_3 = self.authorized_client.get(self.URL_NAMES['INDEX'])
        self.assertNotEqual(response_1.content, response_3.content)

    def test_authorized_client_can_follow_and_unfollow(self):
        """ Тест проверяет, что авторизованный может подписаться и отписаться,
        а неавторизованный - нет"""
        Follow.objects.all().delete()
        self.authorized_client.get(self.URL_NAMES['PROFILE_FOLLOW'])
        follow = Follow.objects.filter(
            user=self.user_not_author,
            author=self.user
            )
        exist = follow.exists()
        self.assertFalse(exist)
        self.not_author.get(self.URL_NAMES['PROFILE_FOLLOW'])
        exist = follow.exists()
        self.assertTrue(exist)
        self.not_author.get(self.URL_NAMES['PROFILE_UNFOLLOW'])
        exist = follow.exists()
        self.assertFalse(exist)

    def test_follow_index_after_author_create_post(self):
        """ Тест проверяет, что пост любимого автора
        появляется в ленте избранных"""
        self.not_author.get(self.URL_NAMES['PROFILE_FOLLOW']
            )
        Post.objects.all().delete()
        Post.objects.create(
            text='Post text',
            author=self.user,
        )
        response = self.not_author.get(self.URL_NAMES['FOLLOW'])
        posts_count = response.context['paginator'].object_list.count()
        self.assertEqual(posts_count, 1)

    def test_only_authorized_client_can_comment_post(self):
        """ Тест проверяет, что авторизованный пользователь
        может комментировать, а неавторизованный - нет"""
        self.assertFalse(Comment.objects.all().exists())
        form_data = {
            'text': 'comment',
        }
        guest_response = self.guest_client.post(
            self.URL_NAMES['COMMENT'],
            data=form_data,
            Follow=True,
            )
        self.assertEqual(guest_response.status_code, 302)
        self.assertIn('/auth/login/', guest_response.url)
        self.assertFalse(Comment.objects.all().exists())
        authorized_response = self.authorized_client.post(
            self.URL_NAMES['COMMENT'],
            data=form_data,
            Follow=True,
            )
        self.assertEqual(authorized_response.status_code, 302)
        self.assertTrue(Comment.objects.all().exists())

    def test_author_cat_delete_yourself_comment(self):
        """ Тест проверяет, что комментарий удаляется -
        самостятельная работа"""
        comment = Comment.objects.create(
            text='comment',
            author=self.user,
            post=self.post,
        )
        self.authorized_client.post(
            reverse('delete_comment',
            args=[self.user.username, comment.post.id, comment.id],
            ),
            follow=True,
        )
        self.assertFalse(Comment.objects.all().exists())
