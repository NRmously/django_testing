from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from notes.models import Note


class BaseTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author = User.objects.create(username='Другой юзер')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.note = Note.objects.create(
            title='Note Title',
            text='Note Text',
            slug='note1',
            author=cls.author,
        )
        cls.form_data = {
            'title': 'Test Title',
            'text': 'Test Text',
            'slug': 'test-slug'
        }
        cls.url_names = {
            'home': reverse('notes:home'),
            'login': reverse('users:login'),
            'logout': reverse('users:logout'),
            'signup': reverse('users:signup'),
            'add_note': reverse('notes:add'),
            'list_notes': reverse('notes:list'),
            'success': reverse('notes:success'),
            'edit': reverse('notes:edit', args=[cls.note.slug]),
            'detail': reverse('notes:detail', args=[cls.note.slug]),
            'delete': reverse('notes:delete', args=[cls.note.slug]),
        }
