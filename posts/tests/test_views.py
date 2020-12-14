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
        for reverse_name, template in TEMPLATE_NAMES.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_edit_show_correct_context(self):
        """ Тест проверяет контекст страницы создания и редактирования поста"""
        url_names = {
            'post_edit': self.URL_NAMES['POST_EDIT'],
            'new_post': self.URL_NAMES['NEW_POST'],
        }
        for name, url in url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertIn('form', response.context)
                if name == 'post_edit':
                    self.assertIn('post', response.context)

    def test_page_context_include_image(self):
        """ Тестирование контекста страницы на наличие картинки """
        uploaded = SimpleUploadedFile(
            name='Тестовая картинка',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        Post.objects.all().delete()
        """ Насчёт замечания по указанию самозаполняемых полей:
        если этого не делать, то запрос страницы поста выдаёт 404 код
        и только явное указание id позволяет получить 200 код """
        post_with_image = Post.objects.create(
            id=1,
            text='Post text',
            author=self.user,
            group=self.group,
            image=uploaded,
            )
        responses = {
            'post': self.URL_NAMES['POST'],
            'index': self.URL_NAMES['INDEX'],
            'profile': self.URL_NAMES['PROFILE'],
            'group': self.URL_NAMES['GROUP'],
        }
        for name, url in responses.items():
            with self.subTest(name=name):
                response = self.not_author.get(url)
                if name == 'post':
                    post_image = response.context['post'].image
                else:
                    post_image = response.context.get('page')[0].image
                self.assertEqual(post_with_image.image, post_image)

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
        self.assertTrue(Follow.objects.exists())

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

    def test_follow_index_after_author_create_post(self):
        """ Тест проверяет, что пост любимого автора
        появляется в ленте избранных"""
        Follow.objects.create(
            user=self.user_not_author,
            author=self.user
        )
        Post.objects.all().delete()
        post = Post.objects.create(
            text='Post text',
            author=self.user,
        )
        response = self.not_author.get(self.URL_NAMES['FOLLOW'])
        response_post = response.context['page'][0]
        self.assertEqual(post.text, response_post.text)
        self.assertEqual(post.author, response_post.author)

    def test_only_guest_client_can_not_comment_post(self):
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

    def test_only_authorized_client_can_comment_post(self):
        """ Тест проверяет, что авторизованный пользователь
        может комментировать"""
        self.assertFalse(Comment.objects.all().exists())
        form_data = {
            'text': 'comment',
        }
        authorized_response = self.authorized_client.post(
            self.URL_NAMES['COMMENT'],
            data=form_data,
            Follow=True,
            )
        self.assertEqual(authorized_response.status_code, 302)
        self.assertTrue(Comment.objects.all().exists())
        comment = Comment.objects.get(id=1)
        self.assertEqual(form_data['text'], comment.text)
        self.assertEqual(self.user, comment.author)
        self.assertEqual(self.post.id, comment.post.id)

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

    def test_pages_show_correct_context(self):
        """ Шаблоны сформированы с правильным контекстом"""
        url_names = [
            self.URL_NAMES['INDEX'],
            self.URL_NAMES['GROUP'],
            self.URL_NAMES['PROFILE'],
            self.URL_NAMES['POST'],
        ]
        for url in url_names:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                if 'page' in response.context:
                    post_context = response.context['page'][0]
                else:
                    post_context = response.context[0]['post']
                self.assertEqual(post_context, self.post)

    def test_pages_show_correct_context_with_group(self):
        """ Шаблоны сформированы с правильным контекстом группы"""
        url_names = [
            self.URL_NAMES['INDEX'],
            self.URL_NAMES['GROUP'],
            self.URL_NAMES['PROFILE'],
            self.URL_NAMES['POST'],
        ]
        for url in url_names:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                if 'page' in response.context:
                    post_context = response.context['page'][0].group.title
                else:
                    post_context = response.context[0]['post'].group.title
                self.assertEqual(post_context, self.post.group.title)

    def test_pages_show_correct_context_with_author(self):
        """ Шаблоны сформированы с правильным контекстом автора"""
        url_names = [
            self.URL_NAMES['INDEX'],
            self.URL_NAMES['GROUP'],
            self.URL_NAMES['PROFILE'],
            self.URL_NAMES['POST'],
        ]
        for url in url_names:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                if 'page' in response.context:
                    post_context = response.context['page'][0].author
                else:
                    post_context = response.context[0]['post'].author
                self.assertEqual(post_context, self.user)
