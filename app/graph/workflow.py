import time
from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from app.graph.state import SupportAgentState
from app.graph.nodes import (
    intent_classifier_node,
    rag_retriever_node,
    reply_drafter_node,
    escalation_router_node
)


def build_graph():
    """
    Constructs and compiles the LangGraph State Graph.
    Flow: START -> intent_classifier -> rag_retriever -> reply_drafter -> escalation_router -> END
    """
    builder = StateGraph(SupportAgentState)

    # Add Nodes
    builder.add_node("intent_classifier", intent_classifier_node)
    builder.add_node("rag_retriever", rag_retriever_node)
    builder.add_node("reply_drafter", reply_drafter_node)
    builder.add_node("escalation_router", escalation_router_node)

    # Add Edges (Linear DAG execution path)
    builder.add_edge(START, "intent_classifier")
    builder.add_edge("intent_classifier", "rag_retriever")
    builder.add_edge("rag_retriever", "reply_drafter")
    builder.add_edge("reply_drafter", "escalation_router")
    builder.add_edge("escalation_router", END)

    return builder.compile()


# Global compiled graph instance
agent_app = build_graph()


def run_agent_pipeline(customer_input: str, customer_id: str = "user_anon", tweet_id: str = None) -> Dict[str, Any]:
    """
    Executes the full agent graph pipeline for an incoming customer request.
    """
    start_time = time.time()

    initial_state: SupportAgentState = {
        "customer_input": customer_input,
        "customer_id": customer_id,
        "tweet_id": tweet_id,
        "intent": None,
        "intent_confidence": 0.0,
        "intent_reasoning": "",
        "grounded_sources": [],
        "max_retrieval_score": 0.0,
        "is_retrieval_confident": False,
        "draft_reply": "",
        "decision": None,
        "escalation_reason": "",
        "escalation_confidence": 0.0,
        "execution_time_ms": 0.0
    }

    final_state = agent_app.invoke(initial_state)
    elapsed_ms = (time.time() - start_time) * 1000.0
    final_state["execution_time_ms"] = round(elapsed_ms, 2)

    return final_state
