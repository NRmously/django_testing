from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

from .conftest import url_reverse

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    (
        (
            url_reverse.get('home'),
            pytest.lazy_fixture('not_author_client'),
            HTTPStatus.OK
        ),
        (
            url_reverse.get('detail'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            url_reverse.get('login'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            url_reverse.get('logout'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            url_reverse.get('signup'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            url_reverse.get('edit'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            url_reverse.get('delete'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            url_reverse.get('edit'),
            pytest.lazy_fixture('not_author_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            url_reverse.get('delete'),
            pytest.lazy_fixture('not_author_client'),
            HTTPStatus.NOT_FOUND
        ),
    ),
)
def test_pages_availability(
    url, parametrized_client, expected_status, comment
):
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (url_reverse.get('edit'), url_reverse.get('delete')),
)
def test_redirect_for_anonymous_client(client, url, comment):
    expected_url = f"{url_reverse.get('login')}?next={url}"
    response = client.get(url)
    assertRedirects(response, expected_url)
