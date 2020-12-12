from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class TestSettings(TestCase):

    @classmethod
    def setUpClass(cls):
        """Создание объектов.
        Объекты будут импортироваться в другие тесты"""
        super().setUpClass()
        cls.user = User.objects.create(
            username='Author'
            )
        cls.user_not_author = User.objects.create(
            username='Not author'
            )
        cls.group = Group.objects.create(
            title='Tittle',
            description='Description'
            )
        cls.group_edit = Group.objects.create(
            title='Edit group',
            description='Another description'
            )
        cls.post = Post.objects.create(
            text='Post text',
            author=cls.user,
            group=cls.group,
            )
        for number in range(2, 13):
            Post.objects.create(
                id=number,
                text="Some text",
                author=cls.user,
                group=cls.group
                )

        site = Site.objects.get(id=1)
        flat_about = FlatPage.objects.create(
            url='/about-author/',
            title='about me',
            content='<b>some content</b>',
            )
        flat_tech = FlatPage.objects.create(
            url='/about-spec/',
            title='about my tech',
            content='<b>some content</b>',
            )
        flat_about.sites.add(site)
        flat_tech.sites.add(site)
        cls.static_pages = ('/about-author/', '/about-spec/')

    def setUp(self):
        super().setUp()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.not_author = Client()
        self.not_author.force_login(self.user_not_author)

        self.URL_NAMES = {
            'INDEX': reverse(
                'index'
                ),
            'GROUP': reverse(
                'group',
                args=[self.group.slug]
                ),
            'NEW_POST': reverse(
                'new_post'
                ),
            'POST_EDIT': reverse(
                'post_edit',
                args=[self.user.username, self.post.id]
                ),
            'PROFILE': reverse(
                'profile',
                args=[self.user.username]
                ),
            'POST': reverse(
                'post',
                args=[self.user.username, self.post.id]
                ),
            'ABOUT-AUTHOR': reverse(
                'about-author'
                ),
            'ABOUT-SPEC': reverse(
                'about-spec'
                ),
            'PAGE_404': reverse(
                '404'
                ),
            'COMMENT': reverse(
                'add_comment',
                args=[self.user.username, self.post.id]
                ),    
            'FOLLOW': reverse(
                'follow_index',
                ),
            'PROFILE_FOLLOW': reverse(
                'profile_follow',
                args=[self.user.username]
                ),
            'PROFILE_UNFOLLOW': reverse(
                'profile_unfollow',
                args=[self.user.username]
                ),
        }
