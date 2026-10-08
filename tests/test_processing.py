from datetime import UTC, datetime, timedelta

from deduplication import remove_duplicate_urls
from models import NewsArticle
from processing import filter_new_articles


def make_article(published_at=None, url="https://example.com/article", title="Test article"):
    return NewsArticle(
        title=title,
        url=url,
        published_at=published_at or datetime.now(UTC),
        summary="Test summary",
        source="Test source",
        embedding_text="",
    )


def test_filter_new_articles_keeps_recent_articles():
    now = datetime.now(UTC)

    articles = [
        make_article(now - timedelta(hours=2)),
        make_article(now - timedelta(hours=10)),
        make_article(now - timedelta(hours=30)),
    ]

    result = filter_new_articles(articles, hours=24)

    assert len(result) == 2


def test_filter_new_articles_rejects_future_articles():
    now = datetime.now(UTC)

    articles = [make_article(now + timedelta(hours=1))]

    result = filter_new_articles(articles, hours=24)

    assert result == []


def test_remove_duplicate_urls():
    articles = [
        make_article(url="https://example.com/a", title="Article A"),
        make_article(url="https://example.com/a", title="Article A duplicate"),
        make_article(url="https://example.com/b", title="Article B"),
    ]

    result = remove_duplicate_urls(articles)

    assert len(result) == 2
    assert result[0].url == "https://example.com/a"
    assert result[1].url == "https://example.com/b"


def test_remove_duplicate_urls_with_empty_list():
    assert remove_duplicate_urls([]) == []


def test_remove_duplicate_urls_when_all_unique():
    articles = [
        make_article(url="https://example.com/a"),
        make_article(url="https://example.com/b"),
    ]

    result = remove_duplicate_urls(articles)

    assert result == articles
