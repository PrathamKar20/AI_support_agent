import numpy as np
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
from app.config import TOP_K_RETRIEVAL, SIMILARITY_THRESHOLD
from app.schemas.models import GroundingSource
from app.data.dataset_loader import load_dataset


class VectorStoreEngine:
    _instance = None

    def __init__(self):
        # Initialize lightweight, highly efficient sentence transformer
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.dataset: List[Dict[str, str]] = load_dataset()
        self.corpus_embeddings = None
        self._build_index()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = VectorStoreEngine()
        return cls._instance

    def _build_index(self):
        """Encodes historical customer queries into embedding vectors."""
        texts = [item["customer_query"] for item in self.dataset]
        if texts:
            self.corpus_embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)

    def retrieve_similar_resolutions(self, query: str, top_k: int = TOP_K_RETRIEVAL) -> List[GroundingSource]:
        """
        Retrieves top-k historical resolution pairs using normalized cosine similarity.
        """
        if self.corpus_embeddings is None or len(self.dataset) == 0:
            return []

        query_embedding = self.model.encode([query], convert_to_numpy=True, normalize_embeddings=True)[0]
        
        # Cosine similarity (since embeddings are L2 normalized, dot product equals cosine similarity)
        scores = np.dot(self.corpus_embeddings, query_embedding)
        
        # Sort indices by score descending
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(scores[idx])
            item = self.dataset[idx]
            results.append(
                GroundingSource(
                    historical_query=item["customer_query"],
                    historical_resolution=item["brand_resolution"],
                    similarity_score=round(score, 4)
                )
            )

        return results
