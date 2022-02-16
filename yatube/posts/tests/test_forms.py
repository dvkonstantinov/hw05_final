from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Post, Group, Comment

User = get_user_model()


class PostFormTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')

        cls.group = Group.objects.create(
            title='Заголовок группы',
            description='Описание группы',
            slug='test-slug'
        )
        cls.group2 = Group.objects.create(
            title='Группа 2',
            description='Описание группы2',
            slug='test-slug-2'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый текст',
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.guest_client = TestCase.client_class()

        cls.form = PostForm()

    def test_create_post_with_image(self):
        post_count = Post.objects.count()
        test_image = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        form_data = {
            'text': 'Второй Тестовый текст',
            'group': self.group.pk,
            'author': self.user,
            'image': test_image,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=False
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(response.status_code, 302, 'Страница с созданным '
                                                    'постом не найдена')
        self.assertEqual(Post.objects.filter(pk=2).exists(), True)

    def test_edit_post(self):
        form_data = {
            'text': 'Обновленный текст',
            'group': self.group2.pk
        }
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        post_text = Post.objects.get(pk=self.post.pk).text
        post_group = Post.objects.get(pk=self.post.pk).group.title
        self.assertEqual(post_text, 'Обновленный текст')
        self.assertEqual(post_group, 'Группа 2')

    def test_comment_form_for_guest(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'ТЕКСТ',
            'author': self.user,
            'post': self.post
        }
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count)
