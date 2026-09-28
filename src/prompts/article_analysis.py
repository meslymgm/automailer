from utils import create_article_id
from models import NewsArticle
ANALYSIS_INSTRUCTIONS = """
You analyse news articles for a personal daily learning breifing.

Classify the article into the most appropriate category from the provided ArticleCategory schema.

Score the article in three dimensions from 1 to 10:

importance_score:
1 = little, broader significance
10 = major societal, economic, technological, educational or international significance

relevance_score:
1 = little value for this daily briefing
10 = highly useful for helping the reader stay informed, culturally current, and intellectually curious

novelty_score:
1 = routine, repetitive, or unsurprising
10 = unusually new, surprising, perspective-expanding, or worth learning about

The briefing is interested in India, interesting practices around the world,human stories, AI and technology, education trends, business and economics, international relations, books and ideas, generational culture, and mental development.

Use Other when the article does not meaningfully fit these interests.

The reason should briefly explain why the scores and category were chosen.
"""


def build_article_input(article: NewsArticle) -> str:
    return f"""
Article ID : {create_article_id(article.url)}

Title: {article.title}

Source: {article.source}

Summary:{article.summary}

"""