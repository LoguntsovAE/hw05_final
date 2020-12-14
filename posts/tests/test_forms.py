import tempfile

from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from posts.models import Post
from posts.tests.test_settings import TestSettings

SMALL_GIF = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                b'\x01\x00\x80\x00\x00\x00\x00\x00'
                b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                b'\x0A\x00\x3B'
            )


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class PostCreateFormTest(TestSettings):

    def test_create_new_post(self):
        """Тест для проверки, что пост создаётся,
        и не попадает в группу, для которой не предназначен,
        а после создания автор перенаправляется на главную страницу"""

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
        Post.objects.all().delete()
        response = self.authorized_client.post(
            self.URL_NAMES['NEW_POST'],
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.URL_NAMES['INDEX'])
        posts = response.context['page']
        self.assertEqual(len(posts), 1)
        self.assertTrue(posts[0].image)
        self.assertEqual(posts[0].text, form_data['text'])
        self.assertEqual(posts[0].group.id, form_data['group'])
        self.assertEqual(posts[0].author, self.user)

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
