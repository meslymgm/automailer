import feedparser
import calendar
from datetime import datetime, timezone

from models import NewsArticle, RSSSource
from sources import RSS_FEEDS


def fetch_feed(source: RSSSource) -> list[NewsArticle]:
    articles = []
    feed = feedparser.parse(source.url)
    for article in feed.entries:
        timestamp = calendar.timegm(article.published_parsed)
        published_at = datetime.fromtimestamp(
             timestamp,
             tz=timezone.utc
        )
        news_article = NewsArticle(
            title= article.title,
            url = article.link,
            source = source.name,
            published_at = published_at,
            summary=article.summary,
            embedding_text = article.title + "\n" + article.summary
        )
        articles.append(news_article)
    return articles

if __name__=="__main__":
    for source in RSS_FEEDS:
        articles = []
        articles.extend(fetch_feed(source))
