from posts.models import Comment
from posts.tests.test_settings import TestSettings


class PostModelTest(TestSettings):

    def test_help_text_from_post(self):
        """ Проверка help_text для полей поста"""
        field_help_texts = {
            'text': 'Введите текст в этом поле',
            'group': 'Необязательно',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).help_text, expected)

    def test_help_text_from_comment(self):
        """ Проверка help_text для поля комментария"""
        verbose_name = Comment._meta.get_field('text').help_text
        self.assertEqual(verbose_name, 'Текст комментария')

    def test_verbose_name_from_post(self):
        """ Проверка verbose_name для полей поста"""
        field_verbose_name = {
            'text': 'Текст поста',
            'group': 'Группа',
        }
        for value, expected in field_verbose_name.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).verbose_name, expected)

    def test_verbose_name_from_comment(self):
        """ Проверка verbose_name для поля комментария"""
        verbose_name = Comment._meta.get_field('text').verbose_name
        self.assertEqual(verbose_name, 'Текст комментария')

    def test_object_name(self):
        """ Тест метода __str___"""
        fields = {
            str(self.post.group): self.post.group.title,
            str(self.post): self.post.text[:15],
        }
        for value, expected in fields.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)
