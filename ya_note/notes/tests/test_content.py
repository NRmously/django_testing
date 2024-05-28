from notes.forms import NoteForm

from .core import BaseTest


class TestContent(BaseTest):

    def test_notes_list_for_author(self):
        response = self.author_client.get(self.url_names['list_notes'])
        self.assertIn('object_list', response.context)
        object_list = response.context['object_list']
        self.assertIsNotNone(object_list)
        self.assertIn(self.note, object_list)

    def test_notes_list_for_not_author(self):
        response = self.not_author_client.get(self.url_names['list_notes'])
        self.assertIn('object_list', response.context)
        object_list = response.context['object_list']
        self.assertIsNotNone(object_list)
        self.assertNotIn(self.note, object_list)

    def test_pages_contains_form_add_and_edit(self):
        urls = [
            ('add_note', self.url_names['add_note']),
            ('edit_note', self.url_names['edit']),
        ]

        for name, url in urls:
            with self.subTest(url=name):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
