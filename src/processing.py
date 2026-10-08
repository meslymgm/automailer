import asyncio
import logging
from datetime import UTC, datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from openai import AsyncOpenAI
from sentence_transformers import SentenceTransformer

from deduplication import remove_duplicate_urls
from google_auth.auth_helper import get_gmail_service
from google_auth.email_renderer import render_briefing_html
from google_auth.email_sender import send_email
from llm import generate_daily_briefing, main
from logging_config import configure_logging
from models import ArticleAnalysis, NewsArticle
from news import fetch_feed
from ranking import calculate_final_Score
from sources import RSS_FEEDS
from utils import create_article_id, create_batches, select_articles

logger = logging.getLogger(__name__)


def filter_new_articles(articles: list[NewsArticle], hours=24) -> list[NewsArticle]:
    new_articles = []
    current_time = datetime.now(UTC)
    for article in articles:
        logger.debug(article)
        difference = current_time - article.published_at
        if timedelta(hours=0) <= difference <= timedelta(hours=hours):
            new_articles.append(article)

    return new_articles


def combine_article_title_summary(articles: list[NewsArticle]):
    for article in articles:
        article.embedding_text = article.title + article.summary


def calculate_similarity_between_articles(
    model_name="sentence-transformers/all-MiniLM-L6-v2", *, articles
):
    model = SentenceTransformer(model_name)
    sentences = []
    for article in articles:
        sentences.append(article.embedding_text)
    embeddings = model.encode(sentences)
    similarities = model.similarity(embeddings, embeddings)
    pairs = []

    for i in range(len(articles)):
        for j in range(i + 1, len(articles)):
            similarity_score = float(similarities[i][j])
            pairs.append(
                {
                    "similarity_score": similarity_score,
                    "article1": articles[i],
                    "article2": articles[j],
                }
            )
    df = pd.DataFrame(pairs)
    df = df.sort_values("similarity_score", ascending=False)
    scores = df["similarity_score"]
    min_val = float(scores.min().item())
    mean_val = float(scores.mean().item())
    median_val = float(scores.median().item())
    mode_val = float(scores.mode()[0].item())  # pandas .mode() returns a Series
    max_val = float(scores.max().item())

    logger.debug(
        f"Min: {min_val} | Mean: {mean_val} | Median: {median_val} | Mode: {mode_val} | max_val: {max_val}"
    )

    # 3. Plot the Chart
    plt.figure(figsize=(8, 5))
    sns.histplot(data=df, x="similarity_score", kde=True, color="skyblue", bins=8)

    # Add vertical lines for central tendencies
    plt.axvline(min_val, color="brown", linestyle=":", linewidth=2, label=f"Min: {min_val:.2f}")
    plt.axvline(mean_val, color="red", linestyle="--", linewidth=2, label=f"Mean: {mean_val:.2f}")
    plt.axvline(
        median_val, color="green", linestyle="-", linewidth=2, label=f"Median: {median_val:.2f}"
    )
    plt.axvline(
        mode_val, color="purple", linestyle="-.", linewidth=2, label=f"Mode: {mode_val:.2f}"
    )
    plt.axvline(max_val, color="blue", linestyle=":", linewidth=2, label=f"Max: {max_val:.2f}")

    # Chart formatting
    plt.title("Data Distribution with Min, Max, Mean, Median, and Mode")
    plt.xlabel("similarity_score")
    plt.ylabel("Count / Frequency")
    plt.legend()
    plt.show()
    # df.to_csv("embeddings_articles.csv")
    percentiles = np.percentile(scores, [50, 75, 90, 95, 99])
    # logger.debug(percentiles)
    return similarities, df, percentiles


async def run_pipeline():
    async with AsyncOpenAI() as client:
        articles = []

        for source in RSS_FEEDS:
            articles.extend(fetch_feed(source))
        recent_articles = filter_new_articles(articles, hours=24)
        articles_unique = remove_duplicate_urls(recent_articles)
        logger.info("Number of articles after url based deduplication: %s", len(articles_unique))
        # similarities, df, percentiles = calculate_similarity_between_articles(articles = articles_unique)
        # clusters = cluster_articles_by_similarity(articles=articles_unique, similarity_matrix=similarities, threshold=0.6)
        # print(len(clusters))
        # print(clusters[0])
        # test_articles = articles_unique[:9]

        batches = create_batches(articles_unique, 10)
        logger.info("Created %s LLM batches", len(batches))

        results: list[list[ArticleAnalysis]] = await main(batches, max_concurrency=2)

        for batch_number, batch_result in enumerate(results, start=1):
            logger.debug(f"\n Batch {batch_number}")

            for analysis in batch_result:
                logger.debug(analysis)

        all_analyses: list[ArticleAnalysis] = [
            analysis for batch_result in results for analysis in batch_result
        ]

        ranked = sorted(all_analyses, key=calculate_final_Score, reverse=True)
        article_by_id = {create_article_id(article.url): article for article in articles_unique}
        articles_selected = select_articles(ranked, 2)
        logger.info("Selected %s articles for final briefing", len(articles_selected))

        # return articles
        for article in articles_selected:
            logger.debug(
                article.category,
                article.importance_score,
                article.relevance_score,
                article.novelty_score,
            )
            logger.debug(article.category)
            # print(article_by_id[article.article_id])

        daily_briefing = await generate_daily_briefing(
            articles_selected, article_by_id, client=client
        )
        logger.debug(daily_briefing)
        daily_briefing_html_body = render_briefing_html(daily_briefing)
        try:
            send_email(
                service=get_gmail_service(),
                recipients=["meslymathews@gmail.com", "bibinkattackan@gmail.com"],
                subject="Today's daily briefing",
                html_body=daily_briefing_html_body,
            )
            logger.info("Email sent successfully")
        except Exception:
            logger.exception("failed to send briefing email: %s ", Exception)
    return daily_briefing


if __name__ == "__main__":
    configure_logging()
    asyncio.run(run_pipeline())
