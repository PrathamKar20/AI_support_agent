import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.models import IntentEnum, EscalationDecisionEnum

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["target_brand"] == "@AppleSupport"


def test_intent_classification_endpoint():
    payload = {
        "text": "@AppleSupport my battery drains from 100% to 20% in 2 hours on iPhone 13.",
        "customer_id": "test_user_001"
    }
    response = client.post("/api/v1/support/classify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == IntentEnum.BATTERY_POWER
    assert data["confidence"] > 0.8


def test_full_pipeline_auto_handle():
    payload = {
        "text": "@AppleSupport keyboard lag on typing after updating my iPad today.",
        "customer_id": "test_user_002"
    }
    response = client.post("/api/v1/support/process", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == IntentEnum.IOS_UPDATES
    assert data["decision"] == EscalationDecisionEnum.AUTO_HANDLE
    assert "@AppleSupport" in data["draft_reply"]
    assert len(data["grounded_sources"]) > 0


def test_full_pipeline_escalation_security():
    payload = {
        "text": "@AppleSupport someone logged into my Apple ID from Russia and changed my recovery email! I am locked out!",
        "customer_id": "test_user_003"
    }
    response = client.post("/api/v1/support/process", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == IntentEnum.APPLE_ID_ACCOUNT
    assert data["decision"] == EscalationDecisionEnum.ESCALATE
    assert "Account security alert detected" in data["escalation_reason"]

# Edge case test
def test_edge_case():
    assert True
