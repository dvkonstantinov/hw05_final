from django.test import TestCase
from django.contrib.auth import get_user_model

from ..models import Post, Group

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='test_user',
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа группа группагруппа',
        )

    def test_models_have_correct_obj_names(self):
        # Насчет self или имени класса и что лучше, в теории написано:
        # К объектам, созданным в методах класса (например, в setUpClass()),
        # синтаксически правильно обращаться через имя класса; например,
        # обращение к объекту task должно выглядеть так: TaskModelTest.task
        # НО мне самому больше нравится self, так что исправлю
        group = self.group
        expected_grp_name = group.title
        post = self.post
        expected_pst_name = post.text[:15]
        self.assertEqual(expected_grp_name, str(group), 'Название группы '
                                                        'неверное')
        self.assertEqual(expected_pst_name, str(post), 'Название поста '
                                                       'неверное')

    def test_models_post_have_corr_verbose_names(self):
        post = self.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)
