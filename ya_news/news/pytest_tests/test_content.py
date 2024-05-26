import pytest

from django.conf import settings

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, setup_homepage_data, home_url):
    response = client.get(home_url)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, setup_homepage_data, home_url):
    response = client.get(home_url)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_order_comments(client, setup_detail_page_data):
    response = client.get(setup_detail_page_data['detail_url'])
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, setup_detail_page_data):
    response = client.get(setup_detail_page_data['detail_url'])
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(client, setup_detail_page_data):
    client.force_login(setup_detail_page_data['author'])
    response = client.get(setup_detail_page_data['detail_url'])
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
