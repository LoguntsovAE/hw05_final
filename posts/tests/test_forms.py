import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse

from posts.models import Post
from posts.tests.test_settings import TestSettings


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class PostCreateFormTest(TestSettings):

    def test_create_new_post(self):
        """Тест для проверки, что пост создаётся,
        и не попадает в группу, для которой не предназначен,
        а после создания автор перенаправляется на главную страницу"""
        small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                b'\x01\x00\x80\x00\x00\x00\x00\x00'
                b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='test.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Создание нового поста',
            'group': self.group.id,
            'image': uploaded
            # точно ли пост с картинкой?
        }
        Post.objects.all().delete()
        response = self.authorized_client.post(
            self.URL_NAMES['NEW_POST'],
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.URL_NAMES['INDEX'])
        post = response.context.get('page')[0]
        self.assertTrue(post)
        # Предыдущий способ тестирования
        # self.assertEqual(len(post), 1)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group_id, form_data['group'])
        # Проверка, что картинка есть в ответе
        self.assertTrue(response.context.get('page').object_list[0].image)
        self.assertNotEqual(post.group.id, self.group_edit)

    def test_edit_post(self):
        """Тест для проверки, что пост изменяется после редактирования"""
        form_data = {
            "text": "Новый текст",
            "group": self.group_edit.id,
        }
        response = self.authorized_client.post(
            reverse("post_edit", args=[self.user, self.post.id]),
            data=form_data,
            follow=True,
        )
        post = response.context['post']
        self.assertEqual(post.text, form_data["text"])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group.id, form_data["group"])
