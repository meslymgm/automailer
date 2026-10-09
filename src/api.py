from fastapi import FastAPI
from pydantic import BaseModel

from news import fetch_feed
from processing import filter_new_articles, run_pipeline
from sources import RSS_FEEDS

app = FastAPI()


class FilterRequest(BaseModel):
    hours: int = 24


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/articles/filter")
def filter_articles(request: FilterRequest):
    all_articles = []

    for source in RSS_FEEDS:
        articles = fetch_feed(source)
        all_articles.extend(articles)

    recent_articles = filter_new_articles(all_articles, hours=request.hours)
    return {
        "hours": request.hours,
        "article_count": len(recent_articles),
        "articles": [
            {
                "title": article.title,
                "url": article.url,
                "source": article.source,
                "published_at": article.published_at,
            }
            for article in articles
        ],
    }


@app.post("/generate_daily_briefing")
async def generate_daily_briefing():
    briefing = await run_pipeline()
    return briefing
