from http import HTTPStatus
import pytest
from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, setup_comment_creation_data):
    client.post(setup_comment_creation_data['url'], data=setup_comment_creation_data['form_data'])
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_can_create_comment(setup_comment_creation_data):
    response = setup_comment_creation_data['auth_client'].post(
        setup_comment_creation_data['url'],
        data=setup_comment_creation_data['form_data']
    )
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f"{setup_comment_creation_data['url']}#comments"
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == setup_comment_creation_data['form_data']['text']
    assert comment.news == setup_comment_creation_data['news']
    assert comment.author == setup_comment_creation_data['user']


@pytest.mark.django_db
def test_user_cant_use_bad_words(setup_comment_creation_data):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = setup_comment_creation_data['auth_client'].post(
        setup_comment_creation_data['url'],
        data=bad_words_data
    )
    assert 'form' in response.context
    assert WARNING in response.context['form'].errors['text']
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_author_can_delete_comment(setup_comment_edit_delete_data):
    response = setup_comment_edit_delete_data['author_client'].delete(
        setup_comment_edit_delete_data['delete_url']
    )
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == setup_comment_edit_delete_data['url_to_comments']
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(setup_comment_edit_delete_data):
    response = setup_comment_edit_delete_data['reader_client'].delete(
        setup_comment_edit_delete_data['delete_url']
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
def test_author_can_edit_comment(setup_comment_edit_delete_data):
    response = setup_comment_edit_delete_data['author_client'].post(
        setup_comment_edit_delete_data['edit_url'],
        data=setup_comment_edit_delete_data['form_data']
    )
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == setup_comment_edit_delete_data['url_to_comments']
    setup_comment_edit_delete_data['comment'].refresh_from_db()
    assert setup_comment_edit_delete_data['comment'].text == setup_comment_edit_delete_data['form_data']['text']


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(setup_comment_edit_delete_data):
    response = setup_comment_edit_delete_data['reader_client'].post(
        setup_comment_edit_delete_data['edit_url'],
        data=setup_comment_edit_delete_data['form_data']
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    setup_comment_edit_delete_data['comment'].refresh_from_db()
    assert setup_comment_edit_delete_data['comment'].text == 'Текст комментария'
