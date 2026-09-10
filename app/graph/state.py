from typing import TypedDict, List, Optional, Dict, Any
from app.schemas.models import IntentEnum, EscalationDecisionEnum, GroundingSource


class SupportAgentState(TypedDict):
    # Inputs
    customer_input: str
    customer_id: str
    tweet_id: Optional[str]

    # Intent Classifier Outputs
    intent: Optional[IntentEnum]
    intent_confidence: float
    intent_reasoning: str

    # RAG Retriever Outputs
    grounded_sources: List[GroundingSource]
    max_retrieval_score: float
    is_retrieval_confident: bool

    # Reply Drafter Outputs
    draft_reply: str

    # Escalation Router Outputs
    decision: Optional[EscalationDecisionEnum]
    escalation_reason: str
    escalation_confidence: float

    # System Performance
    execution_time_ms: float
