import asyncio
import logging

from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    APITimeoutError,
    AsyncOpenAI,
    InternalServerError,
    RateLimitError,
)
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from models import ArticleAnalysis, ArticleAnalysisBatch, DailyBriefing, NewsArticle
from prompts.article_analysis import ANALYSIS_INSTRUCTIONS, build_article_batch_input
from prompts.daily_briefing import BRIEFING_INSTRUCTIONS, build_briefing_input

logger = logging.getLogger(__name__)

load_dotenv()
client = AsyncOpenAI()


@retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential_jitter(initial=1, max=10),
    retry=retry_if_exception_type(
        (APIConnectionError, APITimeoutError, RateLimitError, InternalServerError)
    ),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
async def analyse_article_batch(
    articles: list[NewsArticle], client=client
) -> list[ArticleAnalysis]:
    response = await client.responses.parse(
        model="gpt-5.6-luna",
        input=[
            {"role": "system", "content": ANALYSIS_INSTRUCTIONS},
            {"role": "user", "content": build_article_batch_input(articles)},
        ],
        text_format=ArticleAnalysisBatch,
    )
    event = response.output_parsed
    if event is None:
        raise ValueError("Article analysis response could not be parsed")
    return event.analyses


async def process_batch(batch, semaphore):
    async with semaphore:
        return await analyse_article_batch(batch)


async def main(batches, max_concurrency: int = 3) -> list[list[ArticleAnalysis]]:
    semaphore = asyncio.Semaphore(max_concurrency)
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(process_batch(batch, semaphore)) for batch in batches]
    results = [task.result() for task in tasks]
    return results


async def generate_daily_briefing(selected_analyses, article_by_id, client=client) -> DailyBriefing:
    response = await client.responses.parse(
        model="gpt-5.6-luna",
        input=[
            {"role": "system", "content": BRIEFING_INSTRUCTIONS},
            {"role": "user", "content": build_briefing_input(selected_analyses, article_by_id)},
        ],
        text_format=DailyBriefing,
    )
    if response.output_parsed is None:
        raise ValueError("Daily briefing response could not be parsed")
    return response.output_parsed
