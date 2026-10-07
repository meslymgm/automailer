from datetime import datetime

from utils import create_article_id, create_batches
from models import NewsArticle


def test_create_article_id_is_deterministic():
    url = "https://example.com/article"
    id_1 = create_article_id(url)
    id_2 = create_article_id(url)

    assert id_1 == id_2


def test_different_urls_produce_different_ids():
    id_1 = create_article_id("https://example.com/a")
    id_2 = create_article_id("https://example.com/b")

    assert id_1 != id_2


def test_create_batches():
    article_1 = NewsArticle(
        title="First article",
        url="https://example.com/1",
        published_at=datetime(2024, 1, 1, 9, 0, 0),
        summary="Summary 1",
        source="Example News",
        embedding_text="Embedding text 1",
    )
    article_2 = NewsArticle(
        title="Second article",
        url="https://example.com/2",
        published_at=datetime(2024, 1, 2, 9, 0, 0),
        summary="Summary 2",
        source="Example News",
        embedding_text="Embedding text 2",
    )
    article_3 = NewsArticle(
        title="Third article",
        url="https://example.com/3",
        published_at=datetime(2024, 1, 3, 9, 0, 0),
        summary="Summary 3",
        source="Example News",
        embedding_text="Embedding text 3",
    )
    article_4 = NewsArticle(
        title="Fourth article",
        url="https://example.com/4",
        published_at=datetime(2024, 1, 4, 9, 0, 0),
        summary="Summary 4",
        source="Example News",
        embedding_text="Embedding text 4",
    )
    article_5 = NewsArticle(
        title="Fifth article",
        url="https://example.com/5",
        published_at=datetime(2024, 1, 5, 9, 0, 0),
        summary="Summary 5",
        source="Example News",
        embedding_text="Embedding text 5",
    )

    items = [article_1, article_2, article_3, article_4, article_5]

    batches = create_batches(items, batch_size=2)

    assert batches == [
        [article_1, article_2],
        [article_3, article_4],
        [article_5],
    ]

def test_create_batches_when_input_is_empty():
    assert create_batches([], batch_size=3) == []

def test_create_batches_when_batch_size_exceeds_input():
    assert create_batches([1, 2], batch_size=10) == [[1, 2]]