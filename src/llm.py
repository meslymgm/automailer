from openai import AsyncOpenAI
from models import NewsArticle, ArticleAnalysis, ArticleAnalysisBatch, DailyBriefing
from prompts.article_analysis import ANALYSIS_INSTRUCTIONS, build_article_batch_input
from prompts.daily_briefing import BRIEFING_INSTRUCTIONS, build_briefing_input
from dotenv import load_dotenv
import asyncio

load_dotenv()
client = AsyncOpenAI()

async def analyse_article_batch(articles: list[NewsArticle], client=client) -> ArticleAnalysis:
    response = await client.responses.parse(
        model = "gpt-5.6-luna",
        input = [
            {
                "role": "system",
                "content": ANALYSIS_INSTRUCTIONS
            },
            {
                "role": "user",
                "content": build_article_batch_input(articles)
            }
        ],
        text_format=ArticleAnalysisBatch
    )
    event = response.output_parsed.analyses
    return event


async def process_batch(batch, semaphore):
    async with semaphore:
        return await analyse_article_batch(batch)

async def main(batches, max_concurrency: int =3):
    semaphore = asyncio.Semaphore(max_concurrency)
    async with asyncio.TaskGroup() as tg:
        tasks = [
            tg.create_task(process_batch(batch, semaphore)) for batch in batches
        ]
    results = [task.result() for task in tasks]
    return results

async def generate_daily_briefing(
    selected_analyses,
    article_by_id,
    client=client
) -> DailyBriefing:

    response = await client.responses.parse(
        model="gpt-5.6-luna",
        input=[
            {
                "role": "system",
                "content": BRIEFING_INSTRUCTIONS
            },
            {
                "role": "user",
                "content": build_briefing_input(
                    selected_analyses,
                    article_by_id
                )
            }
        ],
        text_format=DailyBriefing
    )

    return response.output_parsed



