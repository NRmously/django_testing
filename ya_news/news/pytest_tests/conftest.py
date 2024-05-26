from datetime import timedelta
import pytest

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

User = get_user_model()


@pytest.fixture
def reverse_urls():
    urls = {
        'home': 'news:home',
        'detail': 'news:detail',
        'login': 'users:login',
        'logout': 'users:logout',
        'signup': 'users:signup',
    }
    return urls


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def create_news():
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def create_author():
    return User.objects.create(username='Лев Толстой')


@pytest.fixture
def create_reader():
    return User.objects.create(username='Читатель простой')


@pytest.fixture
def create_comment(create_news, create_author):
    return Comment.objects.create(
        news=create_news,
        author=create_author,
        text='Текст комментария'
    )


@pytest.fixture
def setup_data(create_news, create_author, create_reader, create_comment):
    return {
        'news': create_news,
        'author': create_author,
        'reader': create_reader,
        'comment': create_comment,
    }


@pytest.fixture
def setup_homepage_data(db, settings):
    today = timezone.now()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)

    news_list = News.objects.all().order_by('-date')
    return news_list


@pytest.fixture
def create_detail_news():
    return News.objects.create(title='Тестовая новость', text='Просто текст.')


@pytest.fixture
def detail_url(create_detail_news):
    return reverse('news:detail', args=(create_detail_news.id,))


@pytest.fixture
def create_comment_author():
    return User.objects.create(username='Комментатор')


@pytest.fixture
def setup_detail_page_data(
    create_detail_news,
    detail_url,
    create_comment_author
):
    now = timezone.now()
    all_comments = []
    for index in range(10):
        comment = Comment(
            news=create_detail_news,
            author=create_comment_author,
            text=f'Tекст {index}',
            created=now + timedelta(days=index)
        )
        all_comments.append(comment)
    Comment.objects.bulk_create(all_comments)

    comments_list = Comment.objects.filter(
        news=create_detail_news
    ).order_by('-created')

    return {
        'news': create_detail_news,
        'detail_url': detail_url,
        'author': create_comment_author,
        'comments_list': comments_list,
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
def create_comment_author_client():
    author = User.objects.create(username='Автор комментария')
    author_client = Client()
    author_client.force_login(author)
    return author, author_client


@pytest.fixture
def create_reader_client():
    reader = User.objects.create(username='Читатель')
    reader_client = Client()
    reader_client.force_login(reader)
    return reader, reader_client


@pytest.fixture
def create_comment_for_edit_delete(create_news, create_comment_author_client):
    author, _ = create_comment_author_client
    return Comment.objects.create(
        news=create_news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def setup_comment_edit_delete_data(
    create_news,
    create_comment_author_client,
    create_reader_client,
    create_comment_for_edit_delete
):
    author, author_client = create_comment_author_client
    reader, reader_client = create_reader_client
    comment = create_comment_for_edit_delete
    edit_url = reverse('news:edit', args=(comment.id,))
    delete_url = reverse('news:delete', args=(comment.id,))
    news_url = reverse('news:detail', args=(create_news.id,))
    url_to_comments = f'{news_url}#comments'
    form_data = {'text': 'Обновлённый комментарий'}
    return {
        'news': create_news,
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
