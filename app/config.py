import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "app" / "data"
CHROMA_DB_DIR = BASE_DIR / "app" / "data" / "chroma_db"
GOLDEN_SET_PATH = BASE_DIR / "eval" / "golden_set.json"

# Brand Target
TARGET_BRAND = "@AppleSupport"

# Defined Intent Taxonomy for Customer Support
INTENT_CATEGORIES = [
    "Battery & Power",
    "iOS & System Updates",
    "Apple ID & Account Security",
    "App Store & Subscriptions",
    "Hardware & Screen Repair",
    "Audio & Bluetooth Connectivity",
    "General Inquiry & Support"
]

# Escalation Reasons / Criteria
ESCALATION_CRITERIA = {
    "ACCOUNT_LOCKOUT": "Customer account is compromised or locked requiring verification.",
    "HARDWARE_DAMAGE": "Physical damage requiring hardware repair or physical store visit.",
    "REFUND_DISPUTE": "Financial refund request or unauthorized billing dispute.",
    "HIGH_FRUSTRATION": "Severe customer distress or negative sentiment exceeding automated threshold.",
    "UNCERTAIN_RETRIEVAL": "Retrieved historical grounding score below similarity threshold."
}

# RAG Settings
TOP_K_RETRIEVAL = 3
SIMILARITY_THRESHOLD = 0.55

# Ensure directory structures exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)
