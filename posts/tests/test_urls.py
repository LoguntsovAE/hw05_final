from posts.models import Follow
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
author = True
CODE_LIST_AUTHORIZED = [
    ('INDEX', 200, author),
    ('GROUP', 200, author),
    ('NEW_POST', 200, author),
    ('POST_EDIT', 200, author),
    ('POST_EDIT', 302, not author),
    ('PROFILE', 200, author),
    ('POST', 200, author),
    ('ABOUT-AUTHOR', 200, author),
    ('ABOUT-SPEC', 200, author),
    ('PAGE_404', 404, author),
    ('COMMENT', 302, author),
    ('FOLLOW', 200, author),
    ('PROFILE_FOLLOW', 302, author),
    ('PROFILE_UNFOLLOW', 404, author),
    ('PROFILE_UNFOLLOW', 302, not author),
]


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
        for name, code, author in CODE_LIST_AUTHORIZED:
            with self.subTest(name=name):
                if author:
                    request_user = self.authorized_client
                else:
                    request_user = self.not_author
                response = request_user.get(self.URL_NAMES[name])
                self.assertEqual(response.status_code, code)
