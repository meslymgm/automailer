from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock

import pytest

from llm import analyse_article_batch
from models import (
    ArticleAnalysis,
    ArticleAnalysisBatch,
    ArticleCategory,
    NewsArticle,
)


def make_article():
    return NewsArticle(
        title="AI breakthrough",
        url="https://example.com/ai",
        published_at=datetime.now(UTC),
        summary="A new AI system was announced.",
        source="Example",
        embedding_text="",
    )


@pytest.mark.asyncio
async def test_analyse_article_batch_returns_parsed_analyses():
    article = make_article()

    expected_analysis = ArticleAnalysis(
        article_id="abc123",
        category=ArticleCategory.AI_TECH,
        importance_score=8,
        relevance_score=9,
        novelty_score=7,
        reason="Important AI development",
    )

    fake_response = Mock()
    fake_response.output_parsed = ArticleAnalysisBatch(analyses=[expected_analysis])

    fake_client = Mock()
    fake_client.responses.parse = AsyncMock(return_value=fake_response)

    result = await analyse_article_batch([article], client=fake_client)

    assert len(result) == 1
    assert result[0] == expected_analysis
    call = fake_client.responses.parse.await_args

    assert call is not None
    assert call.kwargs["model"] == "gpt-5.6-luna"
    assert call.kwargs["text_format"] == ArticleAnalysisBatch

    input_payload = call.kwargs["input"]

    assert input_payload[0]["role"] == "system"
    assert input_payload[1]["role"] == "user"
