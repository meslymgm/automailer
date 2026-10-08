import hashlib
from collections import defaultdict

from models import ArticleAnalysis, NewsArticle


def create_article_id(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def create_batches(articles: list[NewsArticle], batch_size=10) -> list[list[NewsArticle]]:
    batches = []
    for i in range(0, len(articles), batch_size):
        batches.append(articles[i : i + batch_size])
    return batches


def select_articles(
    analyses: list[ArticleAnalysis],
    max_per_category: int = 2,
) -> list[ArticleAnalysis]:
    selected: list[ArticleAnalysis] = []
    by_category: dict[str, list[ArticleAnalysis]] = defaultdict(list)

    for analysis in analyses:
        category = analysis.category
        if len(by_category[category]) < max_per_category:
            by_category[category].append(analysis)

    for category_analyses in by_category.values():
        selected.extend(category_analyses)

    return selected
