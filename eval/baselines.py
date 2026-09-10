from typing import Dict, Any
from app.schemas.models import IntentEnum, EscalationDecisionEnum
from app.rag.retriever import get_grounded_context


class Baseline0Trivial:
    """
    Trivial Baseline:
    Keyword matching for intent + Static generic template + String length escalation heuristic.
    """
    def process(self, text: str) -> Dict[str, Any]:
        lower_text = text.lower()

        # Keyword intent
        if "battery" in lower_text or "charge" in lower_text:
            intent = IntentEnum.BATTERY_POWER
        elif "update" in lower_text or "ios" in lower_text:
            intent = IntentEnum.IOS_UPDATES
        elif "apple id" in lower_text or "password" in lower_text:
            intent = IntentEnum.APPLE_ID_ACCOUNT
        elif "refund" in lower_text or "charge" in lower_text or "subscription" in lower_text:
            intent = IntentEnum.APP_STORE_SUBSCRIPTIONS
        elif "screen" in lower_text or "repair" in lower_text:
            intent = IntentEnum.HARDWARE_REPAIR
        elif "airpods" in lower_text or "audio" in lower_text:
            intent = IntentEnum.AUDIO_BLUETOOTH
        else:
            intent = IntentEnum.GENERAL_SUPPORT

        # Static draft reply
        draft_reply = "@AppleSupport Thanks for reaching out. Please DM us your device serial number and details so we can assist you."

        # Escalation heuristic (text length or keyword)
        if len(text) > 120 or "urgent" in lower_text or "broken" in lower_text or "refund" in lower_text:
            decision = EscalationDecisionEnum.ESCALATE
            reason = "Trivial heuristic: Message length exceeded 120 characters or contained urgent keywords."
        else:
            decision = EscalationDecisionEnum.AUTO_HANDLE
            reason = "Trivial heuristic: Message length within auto-reply limit."

        return {
            "intent": intent,
            "draft_reply": draft_reply,
            "decision": decision,
            "escalation_reason": reason
        }


class Baseline1SimpleRAG:
    """
    Simple Baseline:
    RAG retrieval without multi-node LangGraph state machine or safety guardrail policies.
    """
    def process(self, text: str) -> Dict[str, Any]:
        # Simple RAG retrieval
        sources, max_score, _ = get_grounded_context(text, top_k=1)
        
        # Simple RAG draft
        if sources:
            draft_reply = sources[0].historical_resolution
        else:
            draft_reply = "@AppleSupport Please check support.apple.com for troubleshooting guides."

        # Simple RAG intent heuristic (defaults to General if low score)
        if sources and max_score > 0.4:
            intent = IntentEnum.GENERAL_SUPPORT
        else:
            intent = IntentEnum.GENERAL_SUPPORT

        # Simple score-only escalation threshold (fails on security & financial policy checks)
        if max_score < 0.5:
            decision = EscalationDecisionEnum.ESCALATE
            reason = "Simple baseline: RAG retrieval score below 0.50 cutoff."
        else:
            decision = EscalationDecisionEnum.AUTO_HANDLE
            reason = "Simple baseline: RAG retrieval score sufficient."

        return {
            "intent": intent,
            "draft_reply": draft_reply,
            "decision": decision,
            "escalation_reason": reason
        }
