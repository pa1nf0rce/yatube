import shutil
import tempfile


from django.contrib.auth import get_user_model
from http import HTTPStatus
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Group, Post, Comment


User = get_user_model()


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='R0man')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_authorized_post_create_form(self):
        """Тестирование создания поста."""
        count_posts = Post.objects.count()
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
        form_data = {
            'text': 'Тестовый текст для формы',
            'group': self.group.id,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), count_posts + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст для формы',
                group=self.group,
                image='posts/small.gif'
            ).exists()
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.user})
        )

    def test_guest_not_post_create_form(self):
        """
        Неавторизованный пользователь не может создать пост.
        """
        form_data = {
            'text': 'Тестовый для формы',
            'group': self.group
        }
        self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertFalse(Post.objects.filter(
            text='Тестовый для формы').exists())

    def test_validation_post_create(self):
        form_data = {
            'text': 'Тестовый',
            'group': self.group
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertFalse(Post.objects.filter(
            text='Тестовый'
        ).exists())
        self.assertFormError(
            response,
            'form',
            'text',
            'Минимальное количество символов - 20'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edition_of_post(self):
        """Тестирование изменения поста"""
        post = Post.objects.create(
            text='Тестовый пост для формы',
            author=self.user,
        )
        gif_edit = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small_edit.gif',
            content=gif_edit,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Новейший текст поста!',
            'group': self.group.id,
            'image': uploaded
        }
        post_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.pk}),
            data=form_data,
            follow=True
        )
        post_edition = Post.objects.get(id=post.pk)
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': post_edition.pk})
        )
        self.assertTrue(
            Post.objects.filter(
                text='Новейший текст поста!',
                group=self.group,
                image='posts/small_edit.gif'
            )
        )
        self.assertEqual(Post.objects.count(), post_count)

    def test_authorized_client_create_comment(self):
        """Тестирование создания поста."""
        comments_count = Comment.objects.count()
        post = Post.objects.create(
            text='Тестовый пост для формы',
            author=self.user,
        )
        form_data = {
            'text': 'Тестовый комментарий'
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text='Тестовый комментарий'
            ).exists()
        )

    def test_guest_not_create_comments(self):
        """
        Неавторизованный полльзователь не может оставить комментарий.
        """
        comments_count  = Comment.objects.count()
        post = Post.objects.create(
            text='Тестовый пост для формы',
            author=self.user,
        )
        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = self.client.post(
            reverse('posts:add_comment', kwargs={'post_id': post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Comment.objects.count(), comments_count)
        self.assertFalse(
            Comment.objects.filter(
                text='Тестовый комментарий'
            ).exists()
        )
