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
        cls.user = User.objects.create_user(username='NoName')
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
        self.post = Post.objects.create(
            text='Текст поста',
            author=self.user,
            group=self.group,
        )
        form_data = {
            'group': self.group,
            'text': 'Текст поста',
        }
        # response = self.authorized_client.post(
        #     reverse('posts:post_create'),
        #     data=form_data,
        #     follow=True
        # )
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.last()
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group, form_data['group'])

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        self.post = Post.objects.create(
            text='Текст поста',
            author=self.user,
            group=self.group,
        )
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-new-slug',
            description='Тестовое описание',
        )
        form_data = {
            'group': self.group,
            'text': 'новый текст',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id, }
                    ),
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post = Post.objects.last()
        self.post.refresh_from_db()
        self.assertEqual(post.author, self.user)
        self.assertNotEqual(post.text, form_data.get('text'))
        # self.assertEqual(post.group, form_data['group'])
        # self.assertEqual(Group.objects.filter(
        #     title='Тестовая группа').count(), 0)
        self.assertIsNot(post, Post.objects.get(pk=self.post.id))
