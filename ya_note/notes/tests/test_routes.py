from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestAvailablePages(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.user = User.objects.create(username='Другой юзер')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
        )

    def test_pages_availability_for_all_users(self):
        urls = (
            ('notes:home'),
            ('users:login'),
            ('users:logout'),
            ('users:signup'),
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_authenticated_user(self):
        urls = (
            ('notes:home'),
            ('notes:add'),
            ('notes:list'),
            ('notes:success'),
            ('users:logout'),
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.user_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_author(self):
        urls = (
            ('notes:detail', self.note.slug),
            ('notes:edit', self.note.slug),
            ('notes:delete', self.note.slug),
        )
        for name, slug in urls:
            with self.subTest(name=name):
                url = reverse(name, kwargs={'slug': slug})
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_add_list_success_for_anonymous_client(self):
        login_url = reverse('users:login')
        urls = (
            ('notes:add'),
            ('notes:list'),
            ('notes:success'),
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_redirect_edit_delete_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name in ('notes:edit', 'notes:delete'):
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_not_available_pages_for_not_author(self):
        urls = (
            ('notes:detail', self.note.slug),
            ('notes:edit', self.note.slug),
            ('notes:delete', self.note.slug),
        )
        for name, slug in urls:
            with self.subTest(name=name):
                url = reverse(name, kwargs={'slug': slug})
                response = self.user_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
