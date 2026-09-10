from typing import Dict, Any
from sentence_transformers import SentenceTransformer
import numpy as np


class LLMAsJudgeRubric:
    """
    Automated LLM-as-Judge Evaluator with Rubric Scoring (1.0 - 5.0)
    Evaluates generated brand replies against ground truth reference replies and context.
    """
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def evaluate_reply(self, customer_query: str, generated_reply: str, reference_reply: str, true_decision: str, pred_decision: str) -> Dict[str, Any]:
        """
        Calculates rubric score metrics:
        - Grounding Score (1-5)
        - Tone & Brand Voice Score (1-5)
        - Escalation Decision Score (1-5)
        - Composite Quality Score (1-5)
        """
        # Embeddings for semantic similarity
        embs = self.model.encode([generated_reply, reference_reply], convert_to_numpy=True, normalize_embeddings=True)
        sem_sim = float(np.dot(embs[0], embs[1]))
        
        # 1. Grounding Score (1-5) based on semantic agreement with historical resolution
        grounding_score = min(5.0, max(1.0, round(1.0 + (sem_sim * 4.0), 2)))

        # 2. Tone & Brand Voice Score (1-5)
        has_greeting = "@AppleSupport" in generated_reply or "Thanks" in generated_reply or "We're here" in generated_reply
        has_actionable_step = any(w in generated_reply for w in ["Settings", "DM", "apple.co", "support.apple", "iforgot", "reset", "check"])
        
        tone_score = 3.0
        if has_greeting:
            tone_score += 1.0
        if has_actionable_step:
            tone_score += 1.0
        tone_score = min(5.0, tone_score)

        # 3. Escalation Decision Score (1-5)
        escalation_score = 5.0 if true_decision == pred_decision else 1.0

        # Composite score
        composite_score = round(0.4 * grounding_score + 0.3 * tone_score + 0.3 * escalation_score, 2)

        return {
            "semantic_similarity": round(sem_sim, 4),
            "grounding_score": grounding_score,
            "tone_score": tone_score,
            "escalation_score": escalation_score,
            "composite_score": composite_score
        }
