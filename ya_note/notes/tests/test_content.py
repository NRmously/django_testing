from django.urls import reverse
from django.test import Client, TestCase
from notes.forms import NoteForm
from notes.models import Note
from django.contrib.auth.models import User


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author = User.objects.create(username='Другой юзер')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            author=cls.author,
            slug='note1',
        )

    def test_notes_list_for_author(self):
        url = reverse('notes:list')
        response = self.author_client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_notes_list_for_not_author(self):
        url = reverse('notes:list')
        response = self.not_author_client.get(url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_pages_contains_form_add(self):
        url = reverse('notes:add')
        response = self.author_client.get(url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_pages_contains_form_edit(self):
        url = reverse('notes:edit', args=[self.note.slug])
        response = self.author_client.get(url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
