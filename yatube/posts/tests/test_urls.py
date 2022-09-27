from django.core.cache import cache
from http import HTTPStatus
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import Post, Group


User = get_user_model()


class PostURLsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user1')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
        )
        cls.index_url = ''
        cls.group_list_url = '/group/test_slug/'
        cls.profile_url = '/profile/user1/'
        cls.post_detail_url = f'/posts/{cls.post.pk}/'
        cls.unknown_url = '/unknown_page/'
        cls.create_url = '/create/'
        cls.post_edit_url = f'/posts/{cls.post.pk}/edit/'
        cls.redirect_login = '/auth/login/?next='

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_posts_urls_exists_at_desired_location(self):
        """Проверка доступа к страницам любому пользователю."""
        address_and_status_code = {
            self.index_url: HTTPStatus.OK,
            self.group_list_url: HTTPStatus.OK,
            self.profile_url: HTTPStatus.OK,
            self.post_detail_url: HTTPStatus.OK,
            self.unknown_url: HTTPStatus.NOT_FOUND,
        }
        for address, status_code in address_and_status_code.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status_code)

    def test_post_create(self):
        response = self.authorized_client.get(self.create_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit(self):
        response = self.authorized_client.get(self.post_edit_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_redirect_anonymous_on_login(self):
        urls_and_redirect = {
            self.create_url:
            self.redirect_login + self.create_url,
            self.post_edit_url:
            self.redirect_login + self.post_edit_url,
        }
        for url, redirect in urls_and_redirect.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, redirect)

    def test_urls_use_correct_template(self):
        urls_and_templates = {
            self.index_url: 'posts/index.html',
            self.group_list_url: 'posts/group_list.html',
            self.profile_url: 'posts/profile.html',
            self.post_detail_url: 'posts/post_detail.html',
            self.create_url: 'posts/create_post.html',
            self.post_edit_url: 'posts/create_post.html',
        }
        for url, template in urls_and_templates.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
