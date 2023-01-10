import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        form_data = {
            'group': self.group.id,
            'text': 'Тестовый текст',
        }
        create_response = self.authorized_client.post(
            reverse('posts:post_create'),
            form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.last()
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.text, form_data['text'])
        # self.assertRedirects(create_response,
        #                      f'/profile/{self.user.username}/')
        self.assertEqual(post.group, self.group)
        self.assertEqual(self.group.posts.count(), 1)
        self.assertEqual(create_response.status_code, HTTPStatus.OK)

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        post = Post.objects.create(
            text='Текст поста',
            author=self.user,
            group=self.group,
        )
        new_group = Group.objects.create(
            title='Тестовая группа',
            slug='test-new-slug',
            description='Тестовое описание',
        )
        new_form_data = {
            'text': 'новый текст',
            'group': new_group.id,
        }
        response_edit = self.authorized_client.post(
            reverse('posts:post_edit', args=(post.id,)),
            new_form_data,
            follow=True
        )
        # self.assertRedirects(response_edit, reverse(
        #     'posts:post_detail', args=(post.id,)))
        post.refresh_from_db()
        self.assertEqual(response_edit.status_code, HTTPStatus.OK)
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.text, new_form_data['text'])
        self.assertEqual(post.group.id, new_group.id)
        self.assertEqual(self.group.posts.count(), 0)
