from posts.tests.test_settings import TestSettings


class PostModelTest(TestSettings):

    def test_help_text(self):
        """ Проверка help_text для полей поста"""
        field_help_texts = {
            'text': 'Введите текст в этом поле',
            'group': 'Необязательно',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).help_text, expected)

    def test_verbose_name(self):
        """ Проверка verbose_name для полей поста"""
        field_verbose_name = {
            'text': 'Текст поста',
            'group': 'Группа',
        }
        for value, expected in field_verbose_name.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).verbose_name, expected)

    def test_object_name(self):
        """ Тест метода __str___"""
        fields = {
            str(self.post.group): self.post.group.title,
            str(self.post): self.post.text[:15],
        }
        for value, expected in fields.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)
