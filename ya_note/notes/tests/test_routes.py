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

        cls.url_names = {
            'home': 'notes:home',
            'login': 'users:login',
            'logout': 'users:logout',
            'signup': 'users:signup',
            'add_note': 'notes:add',
            'list_notes': 'notes:list',
            'success': 'notes:success',
            'detail': 'notes:detail',
            'edit': 'notes:edit',
            'delete': 'notes:delete',
        }

    def test_pages_availability_for_all_users(self):
        urls = ('home', 'login', 'logout', 'signup')
        for name in urls:
            with self.subTest(name=name):
                url = reverse(self.url_names[name])
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_author_and_user(self):
        users = (self.user, self.author)
        user_urls = ('home', 'add_note', 'list_notes', 'success', 'logout')
        author_urls = ('detail', 'edit', 'delete')
        for user in users:
            if user == self.user:
                for name in user_urls:
                    with self.subTest(name=name):
                        url = reverse(self.url_names[name])
                        response = self.user_client.get(url)
                        self.assertEqual(response.status_code, HTTPStatus.OK)
            else:
                for name in author_urls:
                    with self.subTest(name=name):
                        url = reverse(
                            self.url_names[name],
                            args=[self.note.slug]
                        )
                        response = self.author_client.get(url)
                        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse(self.url_names['login'])
        for name in ('add_note', 'list_notes', 'success'):
            with self.subTest(name=name):
                url = reverse(self.url_names[name])
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

        for name in ('edit', 'delete'):
            with self.subTest(name=name):
                url = reverse(self.url_names[name], args=[self.note.slug])
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_not_available_pages_for_not_author(self):
        urls = ('detail', 'edit', 'delete')
        for name in urls:
            with self.subTest(name=name):
                url = reverse(self.url_names[name], args=[self.note.slug])
                response = self.user_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
