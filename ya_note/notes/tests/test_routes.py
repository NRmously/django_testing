from http import HTTPStatus

from django.contrib.auth import get_user_model

from .core import BaseTest

User = get_user_model()


class TestAvailablePages(BaseTest):

    def test_pages_availability_for_all_users(self):
        urls = ('home', 'login', 'logout', 'signup')
        for name in urls:
            with self.subTest(name=name):
                response = self.client.get(self.url_names[name])
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_user(self):
        urls = (
            'detail',
            'edit',
            'delete',
            'home',
            'add_note',
            'list_notes',
            'success',
            'logout',
        )
        for name in urls:
            with self.subTest(name=name):
                response = self.author_client.get(self.url_names[name])
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        for name in ('add_note', 'list_notes', 'success', 'edit', 'delete'):
            with self.subTest(name=name):
                url = f"{self.url_names['login']}?next={self.url_names[name]}"
                response = self.client.get(self.url_names[name])
                self.assertRedirects(response, url)

    def test_not_available_pages_for_not_author(self):
        urls = ('detail', 'edit', 'delete')
        for name in urls:
            with self.subTest(name=name):
                response = self.not_author_client.get(self.url_names[name])
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
