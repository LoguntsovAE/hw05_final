from posts.tests.test_settings import TestSettings
from posts.models import Follow

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
            'POST_EDIT': (200, 302),
            'PROFILE': 200,
            'POST': 200,
            'ABOUT-AUTHOR': 200,
            'ABOUT-SPEC': 200,
            'PAGE_404': 404,
            'COMMENT': 302,
            'FOLLOW': 200,
            'PROFILE_FOLLOW': 302,
            'PROFILE_UNFOLLOW': (404, 302),
    }


class PostURLSTests(TestSettings):

    def test_anonym_user(self):
        """ Проверка доступа страниц для анонимного пользователя """
        for name, code in CODE_LIST_ANONYM.items():
            response = self.guest_client.get(self.URL_NAMES[name])
            with self.subTest(name=name):
                self.assertEquals(response.status_code, code)

    def test_authorized_user(self):
        """ Проверка доступа страниц для авторизованного пользователя """
        Follow.objects.create(
            user=self.user_not_author,
            author=self.user,
        )
        for name, codes in CODE_LIST_AUTHORIZED.items():
            with self.subTest(name=name):
                url_adress = self.URL_NAMES[name]
                response = self.authorized_client.get(url_adress)
                if name in ('POST_EDIT', 'PROFILE_UNFOLLOW'):
                    for code in codes:
                        if code == 302:
                            response = self.not_author.get(url_adress)
                        codes = code
                self.assertEqual(response.status_code, codes)
