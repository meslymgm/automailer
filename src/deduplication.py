from models import NewsArticle

def deduplicate_articles_by_url(articles: list[NewsArticle]) -> list[NewsArticle]:
    """Remove duplicate articles based on their URL while keeping the first occurrence."""
    seen_urls = set()
    unique_articles: list[NewsArticle] = []

    for article in articles:
        if not isinstance(article, NewsArticle):
            continue

        url = article.url
        if url is None:
            unique_articles.append(article)
            continue

        normalized_url = str(url).strip().lower()
        if not normalized_url:
            unique_articles.append(article)
            continue

        if normalized_url in seen_urls:
            continue

        seen_urls.add(normalized_url)
        unique_articles.append(article)

    return unique_articles


def remove_duplicate_urls(existing_articles: list[NewsArticle]) -> list[NewsArticle]:
    """Backward-compatible alias for deduplicating a list of articles by URL."""
    return deduplicate_articles_by_url(existing_articles)


def cluster_articles_by_similarity(articles: list[NewsArticle], similarity_matrix: list[list[float]], threshold: float = 0.8) -> list[list[NewsArticle]]:
    """Group articles into clusters based on similarity score matrix.

    Args:
        articles: List of articles to cluster
        similarity_matrix: 2D matrix of similarity scores between articles (n x n)
        threshold: Minimum similarity score to group articles together (0.0 to 1.0)

    Returns:
        List of article clusters, where each cluster is a list of articles
    """
    if not articles:
        return []

    visited = set()
    clusters: list[list[NewsArticle]] = []

    for i in range(len(articles)):
        if i in visited:
            continue

        cluster = [articles[i]]
        visited.add(i)

        for j in range(i + 1, len(articles)):
            if j in visited:
                continue

            if similarity_matrix[i][j] >= threshold:
                cluster.append(articles[j])
                visited.add(j)

        clusters.append(cluster)
        clusters_ = [cluster for cluster in clusters if len(cluster)>1]

    return clusters_



