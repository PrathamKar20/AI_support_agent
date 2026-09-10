from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class IntentEnum(str, Enum):
    BATTERY_POWER = "Battery & Power"
    IOS_UPDATES = "iOS & System Updates"
    APPLE_ID_ACCOUNT = "Apple ID & Account Security"
    APP_STORE_SUBSCRIPTIONS = "App Store & Subscriptions"
    HARDWARE_REPAIR = "Hardware & Screen Repair"
    AUDIO_BLUETOOTH = "Audio & Bluetooth Connectivity"
    GENERAL_SUPPORT = "General Inquiry & Support"


class EscalationDecisionEnum(str, Enum):
    AUTO_HANDLE = "AUTO_HANDLE"
    ESCALATE = "ESCALATE"


class CustomerRequest(BaseModel):
    text: str = Field(..., description="The raw customer tweet or support message")
    customer_id: Optional[str] = Field(default="user_anon", description="Anonymous user identifier")
    tweet_id: Optional[str] = Field(default=None, description="Optional tweet ID")


class IntentResult(BaseModel):
    intent: IntentEnum = Field(..., description="Classified intent category")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Classification confidence score")
    reasoning: str = Field(..., description="Brief explanation for intent assignment")


class GroundingSource(BaseModel):
    historical_query: str
    historical_resolution: str
    similarity_score: float


class DraftResult(BaseModel):
    draft_reply: str = Field(..., description="Grounded reply draft")
    grounded_sources: List[GroundingSource] = Field(default_factory=list, description="Historical resolutions used as context")


class EscalationResult(BaseModel):
    decision: EscalationDecisionEnum = Field(..., description="AUTO_HANDLE or ESCALATE")
    reason: str = Field(..., description="Stated reason for the auto-handle vs escalation decision")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in escalation route")


class AgentResponse(BaseModel):
    text: str
    intent: IntentEnum
    intent_confidence: float
    intent_reasoning: str
    draft_reply: str
    decision: EscalationDecisionEnum
    escalation_reason: str
    escalation_confidence: float
    grounded_sources: List[GroundingSource]
    execution_time_ms: float


class GoldenExample(BaseModel):
    id: str
    tweet_text: str
    true_intent: IntentEnum
    true_decision: EscalationDecisionEnum
    true_escalation_reason: str
    reference_reply: str
    category_sampling_note: str
