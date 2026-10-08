from models import ArticleAnalysis, ArticleCategory
from ranking import calculate_final_Score


def test_calculate_final_score():
    analysis = ArticleAnalysis(
        article_id="abc123",
        category=ArticleCategory.AI_TECH,
        importance_score=8,
        relevance_score=10,
        novelty_score=6,
        reason="Test",
    )

    result = calculate_final_Score(analysis)

    expected = 0.4 * 10 + 0.35 * 8 + 0.25 * 6

    assert result == expected
