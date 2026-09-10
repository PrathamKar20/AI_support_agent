import re
from typing import Dict, Any, List
from app.graph.state import SupportAgentState
from app.schemas.models import IntentEnum, EscalationDecisionEnum, GroundingSource
from app.rag.retriever import get_grounded_context
from app.config import INTENT_CATEGORIES, SIMILARITY_THRESHOLD


def intent_classifier_node(state: SupportAgentState) -> Dict[str, Any]:
    """
    Classifies customer message into intent taxonomy with explicit reasoning.
    """
    text = state["customer_input"].lower()
    
    # Rule/Keyword Heuristic Matching anchored to Defined Intent Taxonomy
    if any(k in text for k in ["battery", "charge", "charging", "drain", "draining", "power", "hot", "overheating"]):
        intent = IntentEnum.BATTERY_POWER
        reason = "Message contains queries regarding battery health, charging status, or power drain."
        confidence = 0.95
    elif any(k in text for k in ["ios", "update", "freeze", "freezes", "lag", "keyboard", "stutter", "wi-fi", "wifi", "disconnecting"]):
        intent = IntentEnum.IOS_UPDATES
        reason = "Message relates to iOS software update, system performance, or OS network glitches."
        confidence = 0.92
    elif any(k in text for k in ["apple id", "account", "locked", "password", "logged in", "two-factor", "2fa", "verification code", "hacked", "security"]):
        intent = IntentEnum.APPLE_ID_ACCOUNT
        reason = "Message concerns Apple ID authentication, security credentials, or account lockout."
        confidence = 0.96
    elif any(k in text for k in ["charged", "refund", "subscription", "app store", "declined", "payment", "cancel", "trial", "billing"]):
        intent = IntentEnum.APP_STORE_SUBSCRIPTIONS
        reason = "Message addresses App Store purchases, billing disputes, or subscription cancellations."
        confidence = 0.94
    elif any(k in text for k in ["shattered", "screen", "repair", "macbook", "cracked", "physical", "drop", "dropped", "hardware", "warranty"]):
        intent = IntentEnum.HARDWARE_REPAIR
        reason = "Message details physical device damage or hardware repair inquiry."
        confidence = 0.93
    elif any(k in text for k in ["airpods", "bluetooth", "pair", "pairing", "speaker", "crackly", "audio", "silent"]):
        intent = IntentEnum.AUDIO_BLUETOOTH
        reason = "Message reports audio playback or Bluetooth accessory pairing failure."
        confidence = 0.91
    else:
        intent = IntentEnum.GENERAL_SUPPORT
        reason = "General inquiry regarding Apple products, trade-ins, or setup assistance."
        confidence = 0.85

    return {
        "intent": intent,
        "intent_confidence": confidence,
        "intent_reasoning": reason
    }


def rag_retriever_node(state: SupportAgentState) -> Dict[str, Any]:
    """
    Retrieves top-k historical resolution pairs from vector store.
    """
    query = state["customer_input"]
    sources, max_score, is_confident = get_grounded_context(query, top_k=3)
    
    return {
        "grounded_sources": sources,
        "max_retrieval_score": max_score,
        "is_retrieval_confident": is_confident
    }


def reply_drafter_node(state: SupportAgentState) -> Dict[str, Any]:
    """
    Drafts an empathetic, brand-aligned @AppleSupport reply grounded in retrieved historical resolutions.
    """
    sources: List[GroundingSource] = state.get("grounded_sources", [])
    intent = state.get("intent", IntentEnum.GENERAL_SUPPORT)
    
    if sources:
        top_res = sources[0].historical_resolution
        # Format brand reply based on grounded historical pattern
        draft = f"{top_res}"
    else:
        draft = "@AppleSupport Thanks for reaching out. We're here to help! Please send us a Direct Message with your device model and iOS version so we can investigate further."

    return {
        "draft_reply": draft
    }


def escalation_router_node(state: SupportAgentState) -> Dict[str, Any]:
    """
    Evaluates whether message should be auto-handled or escalated to a human agent with a stated reason.
    """
    text = state["customer_input"].lower()
    intent = state.get("intent")
    sources = state.get("grounded_sources", [])
    max_score = state.get("max_retrieval_score", 0.0)

    # 1. Security / Compromised Account Rule
    if intent == IntentEnum.APPLE_ID_ACCOUNT and any(k in text for k in ["hacked", "stolen", "locked", "unauthorized", "logged into"]):
        return {
            "decision": EscalationDecisionEnum.ESCALATE,
            "escalation_reason": "Account security alert detected. Direct human agent intervention required for verification.",
            "escalation_confidence": 0.98
        }

    # 2. Financial Dispute / Refund Escalation Rule
    if any(k in text for k in ["refund", "unauthorized charge", "stolen card", "dispute"]):
        return {
            "decision": EscalationDecisionEnum.ESCALATE,
            "escalation_reason": "Financial transaction or refund request requires human billing specialist review.",
            "escalation_confidence": 0.95
        }

    # 3. Physical Hardware Repair Inspection Rule
    if intent == IntentEnum.HARDWARE_REPAIR and any(k in text for k in ["shattered", "cracked", "water damage", "dropped"]):
        return {
            "decision": EscalationDecisionEnum.ESCALATE,
            "escalation_reason": "Physical hardware damage requires scheduling an Genius Bar appointment or mail-in repair.",
            "escalation_confidence": 0.92
        }

    # 4. Severe Customer Distress / Frustration Rule
    if any(k in text for k in ["terrible", "worst service", "scam", "suing", "unacceptable", "furious"]):
        return {
            "decision": EscalationDecisionEnum.ESCALATE,
            "escalation_reason": "High customer distress detected. Routed to senior escalation manager for priority handling.",
            "escalation_confidence": 0.90
        }

    # 5. Low Retrieval Grounding Confidence Rule
    if max_score < SIMILARITY_THRESHOLD:
        return {
            "decision": EscalationDecisionEnum.ESCALATE,
            "escalation_reason": f"Low retrieval confidence score ({max_score:.2f} < {SIMILARITY_THRESHOLD}). Escalated to human support.",
            "escalation_confidence": 0.88
        }

    # Default: Safe for Auto-Handling
    return {
        "decision": EscalationDecisionEnum.AUTO_HANDLE,
        "escalation_reason": "Query matches standard historical self-service resolution pattern with high grounding confidence.",
        "escalation_confidence": 0.94
    }
