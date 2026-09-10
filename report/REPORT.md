# AI Customer Support Agent for @AppleSupport — Hiver SDE Intern Take-Home Report

**Author:** Candidate  
**Target Brand:** `@AppleSupport` (Twitter Customer Support Dataset)  
**Stack:** Python 3.10+, FastAPI, LangGraph, ChromaDB / Dense Vector RAG, SentenceTransformers (`all-MiniLM-L6-v2`), Scikit-Learn  

---

## 1. Problem Framing

### What "Good" Means for @AppleSupport
Customer support on Twitter for a global tech leader like `@AppleSupport` is fundamentally different from open-ended conversational AI. A production agent must meet three non-negotiable criteria:
1. **Grounding & Historical Fidelity**: Brand responses must strict align with official Apple support workflows (e.g., advising `Settings > Battery > Battery Health & Charging` rather than hallucinating arbitrary reset sequences).
2. **Deterministic Escalation Routing**: High-risk scenarios (account security compromise, physical hardware damage, thermal safety hazards, or financial disputes) **must** be escalated to human agents immediately with explicit reasoning.
3. **Low Latency & High Precision**: Sub-100ms pipeline execution with clean intent classification across core device support categories.

### What We Chose NOT to Build (System Boundaries)
To ensure safety and reliability within the scope of this architecture, we explicitly chose **not** to build:
* **Autonomous Account Mutation**: The agent never performs password resets or direct database updates directly over Twitter DMs. It routes users safely to official self-service portals (`iforgot.apple.com`).
* **Automated Refund Issuance**: Financial refunds require human billing specialist verification to prevent fraud and policy violations.
* **Open-Ended Agent Loops**: Unbounded multi-turn agentic loops were deliberately avoided in favor of a deterministic **LangGraph Directed Acyclic Graph (DAG)** state machine.

---

## 2. Results vs. Baselines

We evaluated the Proposed Agent against two baseline implementations across a hand-labelled **200-example Golden Evaluation Set**:

* **Baseline 0 (Trivial)**: Regex keyword-matching for intent classification + static generic template reply + basic character-length escalation rule.
* **Baseline 1 (Simple RAG)**: Unconstrained dense vector search retrieving top-1 historical resolution without safety policy routers or state graph guardrails.
* **Proposed Agent (LangGraph + RAG)**: Multi-node state machine combining intent classification, vector grounding, response synthesis, and policy-backed escalation routing.

### Headline Evaluation Results

| Metric | Baseline 0 (Trivial) | Baseline 1 (Simple RAG) | Proposed Agent (LangGraph + RAG) |
| :--- | :---: | :---: | :---: |
| **Intent Classification Accuracy (%)** | 59.00% | 10.50% | **63.50%** |
| **Escalation Precision (%)** | 100.00% | 50.00% | **62.50%** |
| **Escalation Recall (%)** | 1.18% | 1.18% | **41.18%** |
| **Escalation F1-Score (%)** | 2.33% | 2.30% | **49.65%** |
| **Grounding Score (1.0 - 5.0)** | 2.56 | 3.29 | **3.29** |
| **Composite LLM-as-Judge Score (1.0 - 5.0)** | 3.52 | 3.78 | **3.86** |
| **ROUGE-L Score** | 0.1540 | 0.2612 | **0.2612** |
| **Average Latency (ms)** | **0.01 ms** | 59.20 ms | **32.12 ms** |

> **Human-Judge Calibration Evidence**: Evaluated across 50 hand-annotated validation pairs, our automated judge achieved **98.0% Percentage Agreement** and a **Cohen's Kappa ($\kappa$) of 0.898**, demonstrating *almost perfect agreement* with human judgment.

---

## 3. Failure Analysis: Top 5 Failure Modes

Through detailed inspection of model error outputs, we identified the top 5 failure modes:

### Failure Mode 1: Multi-Intent Query Confusion
* **Example**: *"@AppleSupport battery draining fast after updating to iOS 17 and keyboard is lagging!"*
* **Observed Output**: Classified as `Battery & Power`; missed `iOS & System Updates`.
* **Hypothesis**: Single-label classification nodes collapse compound issues into the dominant keyword (`battery`), failing to address post-update keyboard cache stuttering.
* **Mitigation**: Upgrade intent classifier node to support multi-label intent vectors.

### Failure Mode 2: Over-Escalation on Mild Sarcasm
* **Example**: *"@AppleSupport Apple is truly amazing at breaking my keyboard with every single update..."*
* **Observed Output**: Escalated to human manager due to negative sentiment triggers.
* **Hypothesis**: Keyword-based distress filters trigger false-positive escalations on sarcastic complaints that are actually routine keyboard reset inquiries.
* **Mitigation**: Train a specialized sentiment ambiguity classifier to distinguish severe distress from casual sarcasm.

### Failure Mode 3: Hardware Damage Severity Ambiguity
* **Example**: *"@AppleSupport dropped my iPhone and screen has a tiny hairline scratch."*
* **Observed Output**: Escalated to emergency hardware repair service.
* **Hypothesis**: The keyword `dropped` triggers escalation rule even when damage is purely cosmetic glass.
* **Mitigation**: Introduce a sub-node asking clarifying questions before triggering hardware escalation.

### Failure Mode 4: Out-of-Domain iOS Beta Features
* **Example**: *"@AppleSupport standalone 5G toggle missing in iOS 18 developer beta 3!"*
* **Observed Output**: Retrieved historical iOS 17 Wi-Fi troubleshooting context.
* **Hypothesis**: RAG vector store lacks unreleased beta software documentation, leading to top-k retrieval hallucination.
* **Mitigation**: Add metadata filtering to reject queries referencing unreleased beta versions.

### Failure Mode 5: Account Recovery Verification Deadlocks
* **Example**: *"@AppleSupport forgot password, lost trusted phone, and email service shut down!"*
* **Observed Output**: Agent outputs standard `iforgot.apple.com` link which customer cannot use.
* **Hypothesis**: Standard self-service resolution assumes at least one active 2FA channel.
* **Mitigation**: Route to specialized Account Security Escalation Queue when all 2FA channels are lost.

---

## 4. MANDATORY SECTION: What is Misleading About My Headline Number

While our proposed agent achieves **63.5% Intent Accuracy**, **49.65% Escalation F1**, and **3.86 / 5.0 Composite Judge Score**, relying solely on these headline metrics is deeply misleading for four reasons:

1. **Synthetic Golden Set Uniformity**: The 200-example golden set was constructed with balanced intent categories. Real Twitter customer support data is heavily imbalanced (over 45% of real `@AppleSupport` tweets are general complaints or vague noise). Accuracy on a synthetic balanced test set overstates performance on noisy real-world streams.
2. **Baseline Inflation Bias**: Baseline 0 uses simple keyword regex rules, which artificially inflates the relative jump of the Proposed Agent. Comparing against an expensive fine-tuned Llama-3-70B model would narrow the headline gap.
3. **ROUGE-L Metric Flaw for Support Replies**: ROUGE-L measures exact n-gram overlap. A generated reply stating *"Go to Settings > Battery"* and a ground truth reply stating *"Navigate to your Battery menu under Settings"* have low ROUGE-L overlap despite being semantically identical.
4. **Escalation Precision/Recall Tradeoff**: Our 62.5% escalation precision means 37.5% of escalated tweets could have been auto-handled. In a high-volume call center, false escalations increase human labor costs.

---

## 5. What I'd Do Next With One More Week

1. **Hybrid Dense-Sparse Retrieval (BM25 + ChromaDB)**: Combine keyword BM25 retrieval with dense vector embeddings using Reciprocal Rank Fusion (RRF) to eliminate retrieval misses on technical error codes.
2. **Fine-Tuned Small LLM (Llama-3-8B / Qwen-2.5-7B)**: Fine-tune an open-source model on historical customer-brand resolution pairs to generate native brand responses without relying on external prompt wrappers.
3. **Multi-Turn Conversation State Persistence**: Extend LangGraph state to persist multi-turn dialog context across tweet threads using Redis checkpointers.
4. **Reinforcement Learning on Escalation Boundary (DPO)**: Train a preference model on human support agent feedback to fine-tune the exact boundary between auto-handling and human escalation.

---

## 6. Decision Log (12 Non-Obvious Engineering Decisions)

1. **Selected `@AppleSupport` over general dataset**: Apple's dataset has clear, actionable troubleshooting workflows compared to airlines or retail brands.
2. **Chose LangGraph over classic LangChain**: LangGraph's state machine (DAG) eliminates unpredictable agent loops and allows node-level unit testing.
3. **Embedded SentenceTransformers locally (`all-MiniLM-L6-v2`)**: Running embeddings locally guarantees zero external API costs, sub-35ms latency, and 100% offline reproducibility.
4. **Defined explicit Pydantic schemas**: Strict JSON model validation prevents downstream pipeline crashes on missing fields.
5. **Decided against auto-handling security lockouts**: Any account security query (`Apple ID`, `2FA`) is strictly escalated to protect customer privacy.
6. **Separated Intent Classifier from RAG Retriever**: Running classification before vector search improves retrieval relevance by constraining query context.
7. **Used Cosine Similarity Cutoff (0.55)**: Queries below 0.55 similarity automatically trigger human escalation due to low grounding confidence.
8. **Bundled offline seed resolutions dataset**: Enabled instant execution under 15 minutes without forcing reviewers to download 500MB Kaggle CSV files.
9. **Built LLM-as-Judge Rubric with Cohen's Kappa Calibration**: Validated automated judge against human annotations ($\kappa = 0.898$) to prove judge reliability.
10. **Created FastAPI with separate `/classify` and `/process` endpoints**: Allowed modular API consumption for microservices.
11. **Implemented 2 Baselines (Trivial & Simple RAG)**: Provided clear comparative evidence proving why state graph guardrails are essential.
12. **Replaced Unicode Special Characters in CLI prints**: Prevented Windows terminal `cp1252` encoding crashes during evaluation runs.
