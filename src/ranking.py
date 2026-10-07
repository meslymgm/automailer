from models import ArticleAnalysis

def calculate_final_Score(analysis: ArticleAnalysis)->float:
    return (
        0.4 * analysis.relevance_score +
        0.35 * analysis.importance_score +
        0.25 * analysis.novelty_score
    )

