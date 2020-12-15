from posts.tests.test_settings import TestSettings

CODE_LIST_ANONYM = {
            'INDEX': 200,
            'GROUP': 200,
            'NEW_POST': 302,
            'POST_EDIT': 302,
            'PROFILE': 200,
            'POST': 200,
            'ABOUT-AUTHOR': 200,
            'ABOUT-SPEC': 200,
            'PAGE_404': 404,
            'COMMENT': 302,
            'FOLLOW': 302,
            'PROFILE_FOLLOW': 302,
            'PROFILE_UNFOLLOW': 302,
        }

CODE_LIST_AUTHORIZED = {
            'INDEX': 200,
            'GROUP': 200,
            'NEW_POST': 200,
            'POST_EDIT': 200,
            'PROFILE': 200,
            'POST': 200,
            'ABOUT-AUTHOR': 200,
            'ABOUT-SPEC': 200,
            'PAGE_404': 404,
            'COMMENT': 302,
            'FOLLOW': 200,
            'PROFILE_FOLLOW': 302,
            'PROFILE_UNFOLLOW': 404,
        }


class PostURLSTests(TestSettings):

    def test_anonym_user(self):
        """ Проверка для анонимного пользователя
            Доступные страницы: главная, группы, профиля,
            поста и статичные страницы
            Недоступны: создание нового поста, редактирование, избранные авторы
        """
        for name, code in CODE_LIST_ANONYM.items():
            response = self.guest_client.get(self.URL_NAMES[name])
            with self.subTest(name=name):
                self.assertEquals(response.status_code, code)

    def test_authorized_user(self):
        """ Проверка для авторизованного пользователя
            Все страницы доступны
            Но страница редактирования поста доступна только его автору
        """
        for name, code in CODE_LIST_AUTHORIZED.items():
            with self.subTest(name=name):
                not_author = self.not_author.get(self.URL_NAMES[name])
                author = self.authorized_client.get(self.URL_NAMES[name])
                if name == 'POST_EDIT' or name == 'PROFILE_UNFOLLOW':
                    self.assertEqual(not_author.status_code, 302)
                self.assertEqual(author.status_code, code)
