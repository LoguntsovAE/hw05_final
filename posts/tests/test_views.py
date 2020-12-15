import tempfile

from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse

from posts.models import Comment, Follow, Post
from posts.settings import POSTS_PER_PAGE
from posts.tests.test_settings import TestSettings

SMALL_GIF = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
             )
UPLOADED = SimpleUploadedFile(
            name='Тестовая картинка',
            content=SMALL_GIF,
            content_type='image/gif'
        )


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class PostPagesTests(TestSettings):

    def test_view_function_uses_correct_template(self):
        """ Тест для проверки того,
        что view функция использует верный шаблон"""
        TEMPLATE_NAMES = {
            self.URL_NAMES['INDEX']: 'index.html',
            self.URL_NAMES['GROUP']: 'posts/group.html',
            self.URL_NAMES['NEW_POST']: 'posts/new.html',
            self.URL_NAMES['POST_EDIT']: 'posts/new.html',
            self.URL_NAMES['PROFILE']: 'posts/profile.html',
            self.URL_NAMES['POST']: 'posts/post.html',
            self.URL_NAMES['ABOUT-AUTHOR']: 'flatpages/default.html',
            self.URL_NAMES['ABOUT-SPEC']: 'flatpages/default.html',
            self.URL_NAMES['FOLLOW']: 'posts/follow.html',
        }
        for url, template in TEMPLATE_NAMES.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_page_context_include_right_post(self):
        """ Тестирование контекста страницы на правильный пост """
        Post.objects.exclude(id=self.post.id).delete()
        post = Post.objects.get(id=1)
        post.image = UPLOADED
        urls = (
            self.URL_NAMES['POST'],
            self.URL_NAMES['INDEX'],
            self.URL_NAMES['GROUP'],
            self.URL_NAMES['FOLLOW'],
        )
        Follow.objects.create(
            user=self.user_not_author,
            author=self.user
        )
        for url in urls:
            with self.subTest(url=url):
                context = self.not_author.get(url).context
                if 'page' in context:
                    response_post = context['page'][0]
                else:
                    response_post = context['post']
                self.assertEqual(response_post, post)

    def test_cache_index_page(self):
        """Тестирование кэша главной страницы"""
        response_1 = self.authorized_client.get(self.URL_NAMES['INDEX'])
        Post.objects.create(
            text='Кэш это круто',
            author=self.user,
        )
        response_2 = self.authorized_client.get(self.URL_NAMES['INDEX'])
        self.assertEqual(response_1.content, response_2.content)
        cache.clear()
        response_3 = self.authorized_client.get(self.URL_NAMES['INDEX'])
        self.assertNotEqual(response_1.content, response_3.content)

    def test_authorized_client_can_not_follow_himself(self):
        """ Тест проверяет, что авторизованный пользователь не может
        подписаться сам на себя """
        Follow.objects.all().delete()
        self.authorized_client.get(self.URL_NAMES['PROFILE_FOLLOW'])
        self.assertFalse(Follow.objects.exists())

    def test_authorized_client_can_follow_another_author(self):
        """ Тест проверяет, что авторизованный пользователь может подписаться
        на другого автора"""
        Follow.objects.all().delete()
        self.not_author.get(self.URL_NAMES['PROFILE_FOLLOW'])
        follow = Follow.objects.filter(
            user=self.user_not_author,
            author=self.user
        ).exists()
        self.assertTrue(follow)

    def test_authorized_client_can_unfollow(self):
        """ Тест проверяет, что авторизованный пользователь может отписаться
        от другого автора"""
        Follow.objects.get_or_create(
            user=self.user_not_author,
            author=self.user
        )
        self.not_author.get(self.URL_NAMES['PROFILE_UNFOLLOW'])
        self.assertFalse(Follow.objects.exists())

    def test_not_authorized_client_can_not_follow(self):
        """ Тест проверяет, что неавторизованный пользователь
        не может подписаться"""
        Follow.objects.all().delete()
        self.guest_client.get(self.URL_NAMES['PROFILE_FOLLOW'])
        self.assertFalse(Follow.objects.exists())

    def test_post_not_in_follow_index_if_user_not_follow_author(self):
        """ Тест проверяет, что пост автора не войдёт в ленту,
        если ты на него не подписан"""
        Follow.objects.all().delete()
        post = Post.objects.create(
            text='Post text',
            author=self.user,
        )
        response = self.not_author.get(self.URL_NAMES['FOLLOW'])
        self.assertNotIn(post, response.context['page'])

    def test_guest_client_can_not_comment_post(self):
        """ Тест проверяет, что неавторизованный пользователь
        не может комментировать"""
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
        self.assertFalse(Comment.objects.all().exists())

    def test_authorized_client_can_comment_post(self):
        """ Тест проверяет, что авторизованный пользователь
        может комментировать"""
        self.assertFalse(Comment.objects.all().exists())
        form_data = {
            'post': self.post,
            'text': 'comment',
            'author': self.user,
        }
        self.authorized_client.post(
            self.URL_NAMES['COMMENT'],
            data=form_data,
            Follow=True,
            )
        response = self.authorized_client.get(self.URL_NAMES['POST'])
        self.assertTrue(Comment.objects.all().exists())
        comment = response.context['comments'][0]
        self.assertEqual(form_data['text'], comment.text)
        self.assertEqual(form_data['author'], comment.author)
        self.assertEqual(form_data['post'], comment.post)

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
                    args=[self.user.username, comment.post.id, comment.id],),
            follow=True,
            )
        self.assertFalse(Comment.objects.all().exists())

    def test_pages_show_right_amount_posts(self):
        """ Тест проверяет количество пост на странице """
        for number in range(2, 13):
            Post.objects.create(
                text="Some text",
                author=self.user,
                group=self.group
                )
        request_urls = (
            self.URL_NAMES['INDEX'],
            self.URL_NAMES['GROUP'],
            self.URL_NAMES['PROFILE'],
        )
        for url in request_urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url).context['paginator']
                posts_count = response.page(1).object_list.count()
                self.assertEqual(posts_count, POSTS_PER_PAGE)

    def test_pages_show_correct_context_with_group(self):
        """ Шаблоны сформированы с правильным контекстом группы"""
        response = self.authorized_client.get(self.URL_NAMES['GROUP'])
        group = response.context['page'][0].group
        self.assertEqual(group, self.group)

    def test_pages_show_correct_context_with_author(self):
        """ Шаблоны сформированы с правильным контекстом автора"""
        url_names = [
            self.URL_NAMES['PROFILE'],
            self.URL_NAMES['POST'],
        ]
        for url in url_names:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                if 'page' in response.context:
                    author = response.context['page'][0].author
                else:
                    author = response.context[0]['post'].author
                self.assertEqual(author, self.user)
