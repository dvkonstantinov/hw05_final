from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Post, Group

User = get_user_model()


class PostUrlTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Заголовок',
            description='Описание группы',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый текст текст текст текст текст',
            pub_date='11.11.2011',
        )
        cls.authorized_client = Client()
        cls.author_client = Client()
        cls.guest_client = TestCase.client_class()
        cls.authorized_client.force_login(cls.user)
        cls.author_client.force_login(cls.author)

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_authorized_and_guest_clients(self):
        urls = [
            '/',
            '/group/test-slug/',
            f'/profile/{self.user}/',
            f'/posts/{self.post.pk}/',
        ]
        clients = [
            self.authorized_client,
            self.guest_client
        ]
        for client in clients:
            for url in urls:
                with self.subTest(url=url):
                    response = client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_unexisting_page(self):
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_url_author_pages(self):
        url = f'/posts/{self.post.pk}/edit/'
        response = self.author_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_only_authorized_client(self):
        url = '/create/'
        response = self.authorized_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_correct_templates(self):
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            f'/profile/{self.user}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertTemplateUsed(response, template)
