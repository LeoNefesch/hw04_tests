import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

# from ..forms import PostForm
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
        # cls.form = PostForm()

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
            # group='Тестовая группа',
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
        # self.assertEqual(Post.objects.count(), 1)
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
        response = self.authorized_client.post(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id, }
        ),
            data={
                'group': 'новая группа',
                'text': 'новый текст',
        },
            follow=True
        )
        edited_post = response.context.get('post')
        edited_group = response.context.get('group')
        self.post.refresh_from_db()
        self.assertEqual(self.post, edited_post)
        self.assertEqual(self.group, edited_group)
        self.assertEqual(Group.objectsfilter(
            title='Тестовая группа').count(), 0)
