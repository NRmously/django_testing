from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.forms import WARNING
from notes.models import Note
from pytils.translit import slugify

User = get_user_model()


class NoteTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author = User.objects.create(username='Другой юзер')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.form_data = {
            'title': 'Test Title',
            'text': 'Test Text',
            'slug': 'test-slug'
        }
        cls.existing_note = Note.objects.create(
            title='Existing Note',
            text='Existing text',
            slug='existing-slug',
            author=cls.author
        )

    def test_user_can_create_note(self):
        posts_count = Note.objects.count()
        url = reverse('notes:add')
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), (posts_count + 1))
        new_note = Note.objects.last()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        posts_count = Note.objects.count()
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), posts_count)

    def test_not_unique_slug(self):
        posts_count = Note.objects.count()
        self.form_data['slug'] = 'existing-slug'
        url = reverse('notes:add')
        response = self.author_client.post(url, data=self.form_data)
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
        url = reverse('notes:add')
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), (posts_count + 1))
        new_note = Note.objects.last()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        url = reverse('notes:edit', args=(self.existing_note.slug,))
        response = self.author_client.post(url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertTrue(Note.objects.filter(pk=self.existing_note.pk).exists())
        self.existing_note.refresh_from_db()
        self.assertEqual(self.existing_note.title, self.form_data['title'])
        self.assertEqual(self.existing_note.text, self.form_data['text'])
        self.assertEqual(self.existing_note.slug, self.form_data['slug'])

    def test_not_author_cant_edit_note(self):
        url = reverse('notes:edit', args=(self.existing_note.slug,))
        response = self.not_author_client.post(url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter(pk=self.existing_note.pk).exists())
        note_from_db = Note.objects.get(id=self.existing_note.id)
        self.assertEqual(self.existing_note.title, note_from_db.title)
        self.assertEqual(self.existing_note.text, note_from_db.text)
        self.assertEqual(self.existing_note.slug, note_from_db.slug)
        self.assertEqual(self.existing_note.author, note_from_db.author)

    def test_author_can_delete_note(self):
        url = reverse('notes:delete', args=(self.existing_note.slug,))
        response = self.author_client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_not_author_cant_delete_note(self):
        url = reverse('notes:delete', args=(self.existing_note.slug,))
        response = self.not_author_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
