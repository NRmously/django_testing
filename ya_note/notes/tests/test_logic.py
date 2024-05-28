from http import HTTPStatus

from django.contrib.auth import get_user_model
from pytils.translit import slugify
from notes.forms import WARNING
from notes.models import Note

from .core import BaseTest

User = get_user_model()


class NoteTests(BaseTest):

    def test_user_can_create_note(self):
        posts_count = Note.objects.count()
        response = self.author_client.post(
            self.url_names['add_note'],
            data=self.form_data
        )
        self.assertRedirects(response, self.url_names['success'])
        self.assertEqual(Note.objects.count(), posts_count + 1)
        new_note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        posts_count = Note.objects.count()
        response = self.client.post(
            self.url_names['add_note'],
            data=self.form_data
        )
        url = f"{self.url_names['login']}?next={self.url_names['add_note']}"
        self.assertRedirects(response, url)
        self.assertEqual(Note.objects.count(), posts_count)

    def test_not_unique_slug(self):
        posts_count = Note.objects.count()
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(
            self.url_names['add_note'],
            data=self.form_data
        )
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.form_data['slug'] + WARNING)
        )
        self.assertEqual(Note.objects.count(), posts_count)

    def test_empty_slug(self):
        posts_count = Note.objects.count()
        self.form_data.pop('slug')
        response = self.author_client.post(
            self.url_names['add_note'],
            data=self.form_data
        )
        self.assertRedirects(response, self.url_names['success'])
        self.assertEqual(Note.objects.count(), (posts_count + 1))
        expected_slug = slugify(self.form_data['title'])
        new_note = Note.objects.get(slug=expected_slug)
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        response = self.author_client.post(
            self.url_names['edit'],
            self.form_data
        )
        self.assertRedirects(response, self.url_names['success'])
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_not_author_cant_edit_note(self):
        response = self.not_author_client.post(
            self.url_names['edit'],
            self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)
        self.assertEqual(self.note.author, note_from_db.author)

    def test_author_can_delete_note(self):
        posts_count = Note.objects.count()
        response = self.author_client.post(self.url_names['delete'])
        self.assertRedirects(response, self.url_names['success'])
        self.assertEqual(Note.objects.count(), posts_count - 1)

    def test_not_author_cant_delete_note(self):
        posts_count = Note.objects.count()
        response = self.not_author_client.post(self.url_names['delete'])
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), posts_count)
