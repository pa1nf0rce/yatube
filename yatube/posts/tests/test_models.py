from django.test import TestCase
from django.contrib.auth import get_user_model
from posts.models import Post, Group


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        group = PostModelTest.group
        self.assertEqual(
            str(group),
            'Тестовая группа',
            ('title не совпадает с ожидаемым результатом')
        )
        post = PostModelTest.post
        self.assertEqual(
            str(post),
            'Тестовый пост',
            ('Текст поста не совпадает с ожидаемым')
        )

    def test_verbose_name(self):
        field = {
            'text': 'Текст поста',
            'group': 'Группа'
        }
        for value, expected in field.items():
            with self.subTest(value=value):
                verbose_name = self.post._meta.get_field(value).verbose_name
                self.assertEqual(verbose_name, expected)

    def test_help_text(self):
        field = {
            'text': 'Текст поста(обязательное поле)',
            'group': 'Выберите группу из представленных (необязательно)'
        }
        for value, expected in field.items():
            with self.subTest(value=value):
                help_text = self.post._meta.get_field(value).help_text
                self.assertEqual(help_text, expected)
