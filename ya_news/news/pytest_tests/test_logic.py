from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from .conftest import url_reverse, FORM_DATA

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, news):
    expected_count = Comment.objects.count()
    client.post(url_reverse.get('detail'), data=FORM_DATA)
    comments_count = Comment.objects.count()
    assert expected_count == comments_count


def test_user_can_create_comment(author_client, author, news):
    expected_count = Comment.objects.count() + 1
    response = author_client.post(url_reverse.get('detail'), data=FORM_DATA)
    comments_count = Comment.objects.count()
    new_comment = Comment.objects.get()
    assertRedirects(response, f"{url_reverse.get('detail')}#comments")
    assert expected_count == comments_count
    assert new_comment.text == FORM_DATA['text']
    assert new_comment.author == author
    assert new_comment.news == news


@pytest.mark.parametrize('word', BAD_WORDS)
def test_user_cant_use_bad_words(author_client, news, word):
    expected_count = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то текст, {word}, еще текст'}
    response = author_client.post(
        url_reverse.get('detail'),
        data=bad_words_data
    )
    comments_count = Comment.objects.count()
    assertFormError(response, form='form', field='text', errors=WARNING)
    assert expected_count == comments_count


def test_author_can_delete_comment(author_client, comment, pk_news):
    expected_count = Comment.objects.count() - 1
    response = author_client.delete(url_reverse.get('delete'))
    comments_count = Comment.objects.count()
    assertRedirects(response, f"{url_reverse.get('detail')}#comments")
    assert expected_count == comments_count


def test_user_cant_delete_foreign_comment(not_author_client, comment):
    expected_count = Comment.objects.count()
    response = not_author_client.delete(url_reverse.get('delete'))
    comments_count = Comment.objects.count()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert expected_count == comments_count


def test_author_can_edit_comment(author, author_client, comment, pk_news):
    expected_count = Comment.objects.count()
    response = author_client.post(url_reverse.get('edit'), data=FORM_DATA)
    assertRedirects(response, f"{url_reverse.get('detail')}#comments")
    comment.refresh_from_db()
    comments_count = Comment.objects.count()
    assert expected_count == comments_count
    assert comment.text == 'Новый текст комментария'
    assert comment.author == author


def test_user_cant_edit_foreign_comment(
    author, not_author_client, comment, pk_news
):
    expected_count = Comment.objects.count()
    response = not_author_client.post(url_reverse.get('edit'), data=FORM_DATA)
    comment.refresh_from_db()
    comments_count = Comment.objects.count()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert expected_count == comments_count
    assert comment.text == 'Текст комментария'
    assert comment.author == author
