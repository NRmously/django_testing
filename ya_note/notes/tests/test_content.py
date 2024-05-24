from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from notes.forms import NoteForm
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
            title='Заголовок',
            text='Текст заметки',
            author=cls.author,
            slug='note1',
        )

    url = reverse('notes:list')


class TestContent(BaseTest):

    def test_notes_list_for_author(self):
        response = self.author_client.get(self.url)
        object_list = response.context['object_list']
        self.assertIsNotNone(object_list)
        if object_list:
            self.assertIn(self.note, object_list)

    def test_notes_list_for_not_author(self):
        response = self.not_author_client.get(self.url)
        object_list = response.context['object_list']
        self.assertIsNotNone(object_list)
        if object_list:
            self.assertIn(self.note, object_list)

    def test_pages_contains_form_add_and_edit(self):
        url_add = reverse('notes:add')
        response_add = self.author_client.get(url_add)
        url_edit = reverse('notes:edit', args=[self.note.slug])
        response_edit = self.author_client.get(url_edit)

        self.assertIn('form', response_add.context)
        self.assertIsInstance(response_add.context['form'], NoteForm)

        self.assertIn('form', response_edit.context)
        self.assertIsInstance(response_edit.context['form'], NoteForm)
