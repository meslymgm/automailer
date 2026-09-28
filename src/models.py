from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

@dataclass
class NewsArticle:
    title: str
    url: str
    published_at: datetime
    summary: str
    source: str
    embedding_text: str

@dataclass
class RSSSource:
    name: str
    url: str

class ArticleCategory(str, Enum):
    INDIA_POLITICS = "India Politics"
    INDIA_POLICIES = "India Policies"
    LIFE_IN_INDIA = "News impacting people living in India, especially Kerala"
    WORLD_PRACTICES = "Interesting Practices Around the World"
    STORIES = "Stories & Human Experience"
    AI_TECH = "AI & Technology"
    EDUCATION = "Education"
    BUSINESS = "Business & Economics"
    INTERNATIONAL = "International Relations"
    BOOKS = "Books & Ideas"
    GENERATIONAL = "Generational Culture"
    MENTAL_DEVELOPMENT = "Mental Development"
    KERALA = "KERALA"
    OTHER = "Other"

class ArticleAnalysis(BaseModel):
    article_id: str
    category: ArticleCategory
    importance_score: int = Field(ge=1, le=10)
    relevance_score: int = Field(ge=1, le=10)
    novelty_score: int = Field(ge=1, le=10)
    reason: str


