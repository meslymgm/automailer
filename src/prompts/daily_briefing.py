from models import ArticleAnalysis, NewsArticle
BRIEFING_INSTRUCTIONS = """
Create a concise daily learning briefing from the supplied
pre-selected articles.

For each article:
- accurately summarize the development
- explain why it matters
- preserve the original meaning
- do not invent facts beyond the supplied article information
- keep the tone informative, clear, and intellectually engaging
- avoid sensationalism

Group items by category where useful.

The reader wants to stay informed about:
India, world practices, AI and technology, education,
business and economics, international relations,
human stories, books and ideas, generational culture,
and mental development.

The briefing should be concise enough to read comfortably
in roughly 5-10 minutes. Closing thought should contain summary of all articles in a concise way.
"""

def build_briefing_input(
    selected_analyses: list[ArticleAnalysis],
    article_by_id: dict[str, NewsArticle]
) -> str:
    articles = """"""
    for article in selected_analyses:
        articles+=f"""
Article category: {article.category}
Title: {article_by_id[article.article_id].title}
Summary: {article_by_id[article.article_id].summary}
Source: {article_by_id[article.article_id].source}
Importance: {article.importance_score}
Relevance: {article.relevance_score}
Novelty: {article.novelty_score}
Reason for scoring: {article.reason}
"""
    return articles