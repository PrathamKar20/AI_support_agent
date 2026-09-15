from typing import List, Tuple
from app.rag.vector_store import VectorStoreEngine
from app.schemas.models import GroundingSource
from app.config import SIMILARITY_THRESHOLD


def get_grounded_context(query: str, top_k: int = 3) -> Tuple[List[GroundingSource], float, bool]:
    """
    Retrieves grounded historical resolutions and computes average/max similarity confidence.
    Returns:
        sources: List of retrieved GroundingSource items
        max_score: Maximum similarity score among top candidates
        is_confident: True if max_score >= SIMILARITY_THRESHOLD
    """
    engine = VectorStoreEngine.get_instance()
    sources = engine.retrieve_similar_resolutions(query, top_k=top_k)

    if not sources:
        return [], 0.0, False

    max_score = sources[0].similarity_score
    is_confident = max_score >= SIMILARITY_THRESHOLD
    return sources, max_score, is_confident

# Score filter helper
def filter_by_score(results, min_score=0.5):
    return [r for r in results if getattr(r, "score", 1.0) >= min_score]
