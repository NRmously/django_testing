from datetime import datetime, timedelta

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone
import pytest

from news.models import Comment, News


url_reverse = {
    'home': reverse('news:home'),
    'detail': reverse('news:detail', args=(1,)),
    'edit': reverse('news:edit', args=(1,)),
    'delete': reverse('news:delete', args=(1,)),
    'login': reverse('users:login'),
    'logout': reverse('users:logout'),
    'signup': reverse('users:signup'),
}


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(title='Заголовок', text='Текст новости')
    return news


@pytest.fixture
def pk_news(news):
    return (news.pk,)


@pytest.fixture
def news_list():
    news_list = News.objects.bulk_create(
        News(
            title=f'Заголовок {i}',
            text='Текст новости',
            date=datetime.today().date() - timedelta(days=i),
        )
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    return news_list


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )
    return comment


@pytest.fixture
def author_comments(author, news):
    for i in range(3):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {i}',
        )
        comment.created = timezone.now() + timedelta(days=i)
        comment.save()
    return author_comments


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст комментария',
    }
