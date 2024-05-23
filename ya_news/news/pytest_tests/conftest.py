from django.urls import reverse
import pytest
from django.contrib.auth import get_user_model
from news.models import Comment, News
from datetime import datetime, timedelta
from django.utils import timezone
from django.test import Client

User = get_user_model()


@pytest.fixture
def setup_data(db):
    news = News.objects.create(title='Заголовок', text='Текст')
    author = User.objects.create(username='Лев Толстой')
    reader = User.objects.create(username='Читатель простой')
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return {
        'news': news,
        'author': author,
        'reader': reader,
        'comment': comment,
    }


@pytest.fixture
def setup_homepage_data(db, settings):
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def setup_detail_page_data(db):
    news = News.objects.create(title='Тестовая новость', text='Просто текст.')
    detail_url = reverse('news:detail', args=(news.id,))
    author = User.objects.create(username='Комментатор')
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return {
        'news': news,
        'detail_url': detail_url,
        'author': author,
    }


@pytest.fixture
def setup_comment_creation_data(db):
    news = News.objects.create(title='Заголовок', text='Текст')
    user = User.objects.create(username='Мимо Крокодил')
    auth_client = Client()
    auth_client.force_login(user)
    url = reverse('news:detail', args=(news.id,))
    form_data = {'text': 'Текст комментария'}
    return {
        'news': news,
        'user': user,
        'auth_client': auth_client,
        'url': url,
        'form_data': form_data,
    }


@pytest.fixture
def setup_comment_edit_delete_data(db):
    news = News.objects.create(title='Заголовок', text='Текст')
    author = User.objects.create(username='Автор комментария')
    author_client = Client()
    author_client.force_login(author)
    reader = User.objects.create(username='Читатель')
    reader_client = Client()
    reader_client.force_login(reader)
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    edit_url = reverse('news:edit', args=(comment.id,))
    delete_url = reverse('news:delete', args=(comment.id,))
    news_url = reverse('news:detail', args=(news.id,))
    url_to_comments = f'{news_url}#comments'
    form_data = {'text': 'Обновлённый комментарий'}
    return {
        'news': news,
        'author': author,
        'author_client': author_client,
        'reader': reader,
        'reader_client': reader_client,
        'comment': comment,
        'edit_url': edit_url,
        'delete_url': delete_url,
        'url_to_comments': url_to_comments,
        'form_data': form_data,
    }
