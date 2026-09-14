from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.models import (
    CustomerRequest,
    AgentResponse,
    IntentResult,
    IntentEnum
)
from app.graph.workflow import run_agent_pipeline
from app.graph.nodes import intent_classifier_node
from app.config import TARGET_BRAND, INTENT_CATEGORIES

app = FastAPI(
    title="Hiver AI Support Agent API",
    description=f"Production AI Customer Support Agent for {TARGET_BRAND} with LangGraph, RAG Grounding, and Guardrail Escalation.",
    version="1.0.0"
)

# Enable CORS for frontend/testing access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {
        "status": "online",
        "brand": TARGET_BRAND,
        "supported_intents": INTENT_CATEGORIES,
        "docs_url": "/docs"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "hiver-ai-support-agent",
        "target_brand": TARGET_BRAND
    }


@app.post("/api/v1/support/process", response_model=AgentResponse)
def process_customer_message(request: CustomerRequest):
    """
    Full AI Support Agent Pipeline:
    1. Classifies intent into defined taxonomy
    2. RAG dense retrieval grounded in historical resolutions
    3. Drafts empathetic @AppleSupport reply
    4. Evaluates auto-handle vs escalation decision with stated reason
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Customer text message cannot be empty.")

    result = run_agent_pipeline(
        customer_input=request.text,
        customer_id=request.customer_id,
        tweet_id=request.tweet_id
    )

    return AgentResponse(
        text=request.text,
        intent=result["intent"],
        intent_confidence=result["intent_confidence"],
        intent_reasoning=result["intent_reasoning"],
        draft_reply=result["draft_reply"],
        decision=result["decision"],
        escalation_reason=result["escalation_reason"],
        escalation_confidence=result["escalation_confidence"],
        grounded_sources=result["grounded_sources"],
        execution_time_ms=result["execution_time_ms"]
    )


@app.post("/api/v1/support/classify", response_model=IntentResult)
def classify_intent_endpoint(request: CustomerRequest):
    """
    Direct endpoint for intent classification only.
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Customer text message cannot be empty.")

    res = intent_classifier_node({"customer_input": request.text, "customer_id": request.customer_id, "tweet_id": request.tweet_id})
    return IntentResult(
        intent=res["intent"],
        confidence=res["intent_confidence"],
        reasoning=res["intent_reasoning"]
    )

# Latency middleware helper
def log_latency():
    pass
