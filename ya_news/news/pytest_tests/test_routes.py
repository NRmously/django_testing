from http import HTTPStatus
import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_pages_availability(client, setup_data):
    urls = (
        ('news:home', None),
        ('news:detail', (setup_data['news'].id,)),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    )
    for name, args in urls:
        url = reverse(name, args=args if args else None)
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_availability_for_comment_edit_and_delete(client, setup_data):
    users_statuses = (
        (setup_data['author'], HTTPStatus.OK),
        (setup_data['reader'], HTTPStatus.NOT_FOUND),
    )
    for user, status in users_statuses:
        client.force_login(user)
        for name in ('news:edit', 'news:delete'):
            url = reverse(name, args=(setup_data['comment'].id,))
            response = client.get(url)
            assert response.status_code == status


@pytest.mark.django_db
def test_redirect_for_anonymous_client(client, setup_data):
    login_url = reverse('users:login')
    for name in ('news:edit', 'news:delete'):
        url = reverse(name, args=(setup_data['comment'].id,))
        redirect_url = f'{login_url}?next={url}'
        response = client.get(url)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == redirect_url