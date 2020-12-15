import tempfile

from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, User

SMALL_GIF = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
             )


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class PostCreateFormTest(TestCase):

    @classmethod
    def setUpClass(cls):
        """Создание объектов.
        Объекты будут наследоваться в другие тесты"""
        super().setUpClass()
        cls.user = User.objects.create(
            username='Author'
            )
        cls.group = Group.objects.create(
            title='Tittle',
            slug='Slug',
            description='Description'
            )
        cls.group_edit = Group.objects.create(
            title='Edit group',
            slug='Edit_slug',
            description='Another description'
            )

    def setUp(self):
        super().setUp()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.post = Post.objects.create(
            text='Post text',
            author=self.user,
            group=self.group,
            )
        self.URL_NAMES = {
            'INDEX': reverse(
                'index'
                ),
            'NEW_POST': reverse(
                'new_post'
                ),
            'POST_EDIT': reverse(
                'post_edit',
                args=[self.user.username, self.post.id]
                ),
            'PROFILE': reverse(
                'profile',
                args=[self.user.username]
                ),
            'POST': reverse(
                'post',
                args=[self.user.username, self.post.id]
                ),
        }

    def test_create_new_post(self):
        """Тест для проверки, что пост создаётся,
        и не попадает в группу, для которой не предназначен,
        а после создания автор перенаправляется на главную страницу"""
        Post.delete(self.post)
        uploaded = SimpleUploadedFile(
            name='test.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Создание нового поста',
            'group': self.group.id,
            'image': uploaded
        }
        response = self.authorized_client.post(
            self.URL_NAMES['NEW_POST'],
            data=form_data,
            follow=True
        )
        self.assertEqual(response.context['paginator'].count, 1)
        self.assertRedirects(response, self.URL_NAMES['INDEX'])
        post = response.context['page'][0]
        self.assertEqual(post.image.size, form_data['image'].size)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.author, self.user)

    def test_edit_post(self):
        """Тест для проверки, что пост изменяется после редактирования"""
        form_data = {
            'text': 'Новый текст',
            'group': self.group_edit.id,
        }
        response = self.authorized_client.post(
            self.URL_NAMES['POST_EDIT'],
            data=form_data,
            follow=True,
        )
        post = response.context['post']
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group.id, form_data["group"])

    def test_new_post_fields(self):
        """ Тест проверяет типы полей формы создания нового поста"""
        response = self.authorized_client.get(self.URL_NAMES['NEW_POST'])
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_comment_field(self):
        """Тест проверяет типы полей формы создания нового комментария """
        response = self.authorized_client.get(self.URL_NAMES['POST'])
        form_field = response.context.get('form').fields.get('text')
        self.assertIsInstance(form_field, forms.fields.CharField)

    def test_post_edit_and_new_post_pages_show_correct_context(self):
        """ Тест проверяет контекст страницы создания и редактирования поста"""
        url_names = {
            'post_edit': reverse(
                'post_edit',
                args=[self.user.username, self.post.id]
                ),
            'new_post': self.URL_NAMES['NEW_POST'],
        }
        for name, url in url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertIn('form', response.context)
                if name == 'post_edit':
                    self.assertIn('post', response.context)
