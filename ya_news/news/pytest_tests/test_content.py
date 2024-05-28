from datetime import date

from django.conf import settings
from django.utils import timezone
import pytest

from news.forms import CommentForm
from .conftest import url_reverse

pytestmark = pytest.mark.django_db


def test_news_count_and_order(client, news_list):
    response = client.get(url_reverse.get('home'))
    assert 'object_list' in response.context
    object_list = list(response.context['object_list'])
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE
    assert isinstance(object_list[0].date, date)
    assert object_list == sorted(
        object_list, key=lambda x: x.date, reverse=True
    )


def test_order_comments(client, news, author_comments):
    response = client.get(url_reverse.get('detail'))
    assert 'news' in response.context
    news = response.context['news']
    all_comments = list(news.comment_set.all())
    assert isinstance(all_comments[0].created, timezone.datetime)
    sorted_comments = sorted(all_comments, key=lambda x: x.created)
    assert all_comments == sorted_comments


def test_anonymous_client_has_no_form(client):
    response = client.get(url_reverse.get('detail'))
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, news):
    response = author_client.get(url_reverse.get('detail'))
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
