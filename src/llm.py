from openai import OpenAI
from models import NewsArticle, ArticleAnalysis
from prompts.article_analysis import ANALYSIS_INSTRUCTIONS, build_article_input
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def analyse_article(article: NewsArticle, client=client) -> ArticleAnalysis:
    response = client.responses.parse(
        model = "gpt-5.6-luna",
        input = [
            {
                "role": "system",
                "content": ANALYSIS_INSTRUCTIONS
            },
            {
                "role": "user",
                "content": build_article_input(article=article)
            }
        ],
        text_format=ArticleAnalysis
    )
    event = response.output_parsed
    return event



