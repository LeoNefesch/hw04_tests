from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        Post.objects.create(
            text='Текст поста',
            pk=5,
            pub_date='Дата публикации',
            author=cls.user,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/NoName/': 'posts/profile.html',
            '/posts/5/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/5/edit/': 'posts/create_post.html',
        }
        self.url_names = {
            '/': HTTPStatus.OK,
            '/group/test-slug/': HTTPStatus.OK,
            '/profile/NoName/': HTTPStatus.OK,
            '/posts/5/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }

    def test_urls_correct_ctatus_code(self):
        """Соответсвие URL-адреса страницы и статуса ответа
        для неавторизованного пользователя."""

        for address, status in self.url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status)

    def test_post_create_url_exists_at_desired_location(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_edit_url_exists_at_desired_location(self):
        """Страница /posts/5/edit/ доступна авторизованному
        пользователю."""
        response = self.authorized_client.get('/posts/5/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_create_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу /create/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    def test_post_edit_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу /posts/5/edit/ перенаправит
        анонимного пользователя на страницу логина.
        """
        response = self.guest_client.get(
            '/posts/5/edit/', follow=True
        )
        self.assertRedirects(
            response, '/auth/login/?next=/posts/5/edit/'
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for address, template in self.templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
