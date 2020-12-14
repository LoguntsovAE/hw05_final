from posts.tests.test_settings import TestSettings


class PostURLSTests(TestSettings):

    def test_anonymous_user(self):
        """ Проверка для анонимного пользователя
            Доступные страницы: главная, группы, профиля,
            поста и статичные страницы
            Недоступны: создание нового поста, редактирование, избранные авторы
        """
        for name, value in self.URL_NAMES.items():
            code = 200
            list_code_302 = (
                'NEW_POST',
                'POST_EDIT',
                'FOLLOW',
                'PROFILE_FOLLOW',
                'PROFILE_UNFOLLOW',
                'COMMENT'
                )
            if name in list_code_302:
                code = 302
            if name == 'PAGE_404':
                code = 404
            response = self.guest_client.get(value)
            with self.subTest(value=name):
                self.assertEquals(response.status_code, code)

    def test_authorized_user(self):
        """ Проверка для авторизованного пользователя
            Все страницы доступны
            Но страница редактирования поста доступна только его автору
        """
        for name, value in self.URL_NAMES.items():
            with self.subTest(url=name):
                response_not_author = self.not_author.get(value)
                response_author = self.authorized_client.get(value)
                response = response_author
                code = 200
                if name == 'POST_EDIT':
                    code = 200
                    self.assertEqual(response_not_author.status_code, 302)
                if name == 'PAGE_404':
                    code = 404
                if name == 'COMMENT':
                    code = 302
                follow_urls = (
                    'PROFILE_FOLLOW',
                    'PROFILE_UNFOLLOW',
                    )
                if name in follow_urls:
                    code = 302
                    response = response_not_author
                self.assertEqual(response.status_code, code)
