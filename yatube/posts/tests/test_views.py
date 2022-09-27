
import shutil
import tempfile

from django import forms
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.conf import settings
from posts.models import Post, Group, Follow
from django.contrib.auth import get_user_model
from django.core.cache import cache


User = get_user_model()


COUNT_CREATE_POSTS = 13
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='R0man')
        cls.group = Group.objects.create(
            title='Тестовое название',
            slug='test_slug',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
            image=uploaded
        )
        cls.group_2 = Group.objects.create(
            title='Тестовое название 2',
            slug='test_slug2',
            description='test'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def check_post_information(self, post):
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group.id, self.post.group.id)
        self.assertEqual(post.image, self.post.image)

    def test_pages_uses_correct_templates(self):
        """URL-адрес использует правильный шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/post_detail.html': (
                reverse(
                    'posts:post_detail',
                    kwargs={'post_id': self.post.pk}
                )
            ),
            'posts/group_list.html': (
                reverse(
                    'posts:group_list',
                    kwargs={'slug': self.group.slug}
                )
            ),
            'posts/profile.html': (
                reverse(
                    'posts:profile',
                    kwargs={'username': self.user.username}
                )
            ),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_uses_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.check_post_information(response.context['page_obj'][0])


    def test_group_posts_uses_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        self.assertEqual(response.context['group'], self.group)
        self.check_post_information(response.context['page_obj'][0])

    def test_post_not_another_group(self):
        self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group_2.slug}
        ))
        count_posts = Post.objects.filter(
            group=self.group_2).count()
        self.assertEqual(count_posts, 0)

    def test_profile_uses_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username}))
        self.check_post_information(response.context['page_obj'][0])
        self.assertEqual(response.context['author'], self.user)

    def test_post_detail_uses_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}))
        self.check_post_information(response.context['post'])

    def test_post_create_uses_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_uses_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.pk}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context['is_edit'], True)

    def test_cache_on_index_page(self):
        post = Post.objects.create(
            text='Текст для тестирование кэша',
            author=self.user
        )
        content = self.authorized_client.get(
            reverse('posts:index')).content
        post.delete()
        content_delete = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertEqual(content, content_delete)
        cache.clear()
        content_after_cache_cleared = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertNotEqual(content, content_after_cache_cleared)

class PostPaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='R0man')
        cls.group = Group.objects.create(
            title='Тестовое название',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.bulk_create([Post(
            text=f'Тестовый пост {i}',
            author=cls.user,
            group=cls.group) for i in range(COUNT_CREATE_POSTS)
        ])

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_page_contains_records(self):
        """
        Проверка: на первой странице 10 постов, но второй - 3.
        """
        address_and_count_posts = {
            reverse('posts:index'): 10,
            (reverse('posts:index') + '?page=2'): 3,
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test_slug'}): 10,
            (reverse(
                'posts:group_list',
                kwargs={'slug': 'test_slug'}) + '?page=2'): 3,
            reverse(
                'posts:profile',
                kwargs={'username': 'R0man'}): 10,
            (reverse(
                'posts:profile',
                kwargs={'username': 'R0man'}) + '?page=2'): 3,
        }
        for address, count_posts in address_and_count_posts.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(
                    len(response.context['page_obj']), count_posts
                )

class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_post = User.objects.create_user(
            username='author_post'
        )
        cls.follower = User.objects.create_user(
            username='noname'
        )
        cls.post = Post.objects.create(
            text='Проверка подписки на автора',
            author=cls.author_post
        )
    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author_post)
        self.authorized_follower = Client()
        self.authorized_follower.force_login(self.follower)
        cache.clear()

    def test_profile_follow_views(self):
        """
        Тестирование подписки на автора один и только один раз.
        """
        count_following = Follow.objects.count()
        self.authorized_follower.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author_post})
        )
        self.assertEqual(Follow.objects.count(), count_following + 1)
        self.authorized_follower.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author_post})
        )
        count_after = Follow.objects.count()
        self.assertEqual(Follow.objects.count(), count_after)

    def test_profile_unfollow_views(self):
        """
        Тестирование отписки от автора один и только один раз.
        """
        Follow.objects.create(
            author=self.author_post,
            user=self.follower
        )
        count_following = Follow.objects.count()
        self.authorized_follower.post(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.author_post}
            )
        )
        self.assertEqual(Follow.objects.count(), count_following - 1)
        count_after = Follow.objects.count()
        self.authorized_follower.post(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.author_post}
            )
        )
        self.assertEqual(Follow.objects.count(), count_after)

    def test_author_cant_following_on_yourself(self):
        count_follow = Follow.objects.count()
        self.authorized_author.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author_post})
        )
        self.assertEqual(Follow.objects.count(), count_follow)

    def test_follow_index_views(self):
        """
        Проверка наличия поста у подписанного пользователя.
        """
        Follow.objects.create(
            author=self.author_post,
            user=self.follower
        )
        response = self.authorized_follower.get(
            reverse('posts:follow_index')
        )
        self.assertIn(self.post, response.context['page_obj'].object_list)

    def test_follow_index_without_following(self):
        response = self.authorized_follower.get(
            reverse('posts:follow_index')
        )
        self.assertNotIn(self.post, response.context['page_obj'].object_list)