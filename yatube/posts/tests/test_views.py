from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Post, Group, Follow
from ..views import NUMBER_OF_POSTS

User = get_user_model()

PAGES_WITH_POST_LIST = [
    reverse('posts:index'),
    reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
    reverse('posts:profile', kwargs={'username': 'user'})
]


class PostPagesTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.another_user = User.objects.create_user(username='user2')
        cls.image = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.image,
            content_type='image/gif'
        )

        cls.group = Group.objects.create(
            title='Заголовок группы',
            description='Описание группы',
            slug='test-slug'
        )
        cls.group2 = Group.objects.create(
            title='Заголовок группы 2',
            description='Описание группы 2',
            slug='test-slug-2'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый текст',
            pub_date='11.11.2011',
            image=cls.uploaded
        )

        cls.authorized_client = Client()
        cls.follow_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.follow_client.force_login(cls.another_user)

    def test_pages_uses_correct_template(self):
        reverses = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'test-slug'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': 'user'}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}
                    ): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}
                    ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in reverses.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        first_obj = response.context['page_obj'][0]
        post_text_0 = first_obj.text
        self.assertEqual(post_text_0, 'Тестовый текст')

    def test_group_post_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
        first_obj = response.context['page_obj'][0]
        post_group_0 = first_obj.group.slug
        self.assertEqual(post_group_0, 'test-slug')

    def test_profile_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'user'}))
        first_obj = response.context['page_obj'][0]
        post_user_0 = first_obj.author.username
        self.assertEqual(post_user_0, 'user')

    def test_post_detail_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}))
        self.assertEqual(response.context['post'].group.title, ('Заголовок '
                                                                'группы'))
        self.assertEqual(response.context['post'].text, 'Тестовый текст')
        self.assertEqual(response.context['post'].pk, 1)

    def test_create_and_edit_post_show_correct_context(self):
        response_edit = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}))
        response_create = self.authorized_client.get(reverse(
            'posts:post_create'))
        responses = [response_edit, response_create]
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for response in responses:
            for value, expected in form_fields.items():
                form_field = response.context['form'].fields[value]
                with self.subTest(value=value):
                    self.assertIsInstance(form_field, expected)

        form_text = response_edit.context['form']['text'].value()
        self.assertEqual(form_text, 'Тестовый текст')

    def test_post_appearance_check(self):

        for page_reverse in PAGES_WITH_POST_LIST:
            response = self.client.get(page_reverse)
            appeared_post_text = response.context['page_obj'][0].text
            self.assertEqual(appeared_post_text, 'Тестовый текст',
                             f'не появился пост на странице {page_reverse}')

        response = self.client.get(reverse('posts:group_list',
                                           kwargs={'slug': 'test-slug-2'}))
        self.assertEqual(len(response.context['page_obj']), 0, (
            'Пост появился в той группе, где появиться не должен'))

    def test_posts_images_appearance_in_db(self):
        self.assertEqual(Post.objects.all().count(), 1)

    def test_posts_images_appearance(self):
        for page in PAGES_WITH_POST_LIST:
            response = self.client.get(page)
            image = response.context['page_obj'][0].image
            self.assertTrue(image)

    def test_post_detail_images_appearance(self):
        response = self.client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}))
        image = response.context['post'].image
        self.assertTrue(image)

    def test_comment_appearance(self):
        form_data = {
            'text': 'ТЕКСТ',
            'author': self.user,
            'post': self.post
        }
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}))
        self.assertEqual(response.context['comments'][0].text, 'ТЕКСТ')

    def test_check_index_page_cache(self):
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        cached_page = response.content
        self.post = Post.objects.create(
            text='Второй пост',
            author=self.user,
            group=self.group,
        )
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(cached_page, response.content)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(cached_page, response.content)

    def test_user_follow_unfollow(self):
        response = self.follow_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user.username}))
        self.assertFalse(response.context['following'])
        response = self.follow_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user.username}))
        response = self.follow_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user.username}))
        self.assertTrue(response.context['following'])
        response = self.follow_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.user.username}))
        response = self.follow_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user.username}))
        self.assertFalse(response.context['following'])

    def test_post_appearance_for_followers(self):
        response = self.follow_client.get(reverse('posts:index'))
        post = response.context['page_obj'][0].text
        self.assertEqual(post, 'Тестовый текст')
        response = self.follow_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user.username}))
        self.post2 = Post.objects.create(
            author=self.user,
            group=self.group,
            text='Новый текст',
            pub_date='21.11.2011',
            image=self.uploaded
        )
        cache.clear()
        response = self.follow_client.get(reverse('posts:index'))
        post = response.context['page_obj'][0].text
        self.assertEqual(post, 'Новый текст')

    def test_unable_follow_yourself(self):
        count_follow = Follow.objects.count()
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user.username}))
        self.assertEqual(Follow.objects.count(), count_follow)

    def test_once_follow_per_user(self):
        self.follow_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user.username}))
        count_follow = Follow.objects.count()
        self.follow_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user.username}))
        self.assertEqual(Follow.objects.count(), count_follow)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='Заголовок группы',
            description='Описание группы',
            slug='test-slug'
        )
        for i in range(1, 16):
            cls.post = Post.objects.create(
                text='Тестовый текст ' + str(i),
                author=cls.user,
                group=cls.group,
            )

    def test_first_page_contains_ten_records(self):
        for page_reverse in PAGES_WITH_POST_LIST:
            response = self.client.get(page_reverse)
            self.assertEqual(len(response.context['page_obj']),
                             NUMBER_OF_POSTS)

    def test_second_page_contains_three_records(self):
        for page_reverse in PAGES_WITH_POST_LIST:
            response = self.client.get(page_reverse + '?page=2')
            self.assertEqual(len(response.context['page_obj']), 5)
