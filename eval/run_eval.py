import json
import time
from pathlib import Path
from typing import Dict, Any, List
from rouge_score import rouge_scorer
from sklearn.metrics import precision_recall_fscore_support, accuracy_score

from app.graph.workflow import run_agent_pipeline
from eval.baselines import Baseline0Trivial, Baseline1SimpleRAG
from eval.judge_rubric import LLMAsJudgeRubric
from eval.human_agreement import calculate_human_judge_agreement
from app.config import GOLDEN_SET_PATH


def evaluate_system(system_name: str, runner_fn, golden_data: List[Dict[str, Any]], judge: LLMAsJudgeRubric) -> Dict[str, Any]:
    """
    Evaluates a system runner on the golden set across all metrics.
    """
    y_true_intent = []
    y_pred_intent = []
    
    y_true_decision = []
    y_pred_decision = []

    grounding_scores = []
    tone_scores = []
    composite_scores = []
    rouge_l_scores = []
    latencies_ms = []

    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)

    for item in golden_data:
        tweet_text = item["tweet_text"]
        true_intent = item["true_intent"]
        true_decision = item["true_decision"]
        ref_reply = item["reference_reply"]

        t0 = time.time()
        res = runner_fn(tweet_text)
        t_elapsed = (time.time() - t0) * 1000.0
        latencies_ms.append(t_elapsed)

        pred_intent = res["intent"].value if hasattr(res["intent"], "value") else str(res["intent"])
        true_intent = true_intent.value if hasattr(true_intent, "value") else str(true_intent)

        pred_reply = res["draft_reply"]
        
        pred_decision = res["decision"].value if hasattr(res["decision"], "value") else str(res["decision"])
        true_decision = true_decision.value if hasattr(true_decision, "value") else str(true_decision)

        y_true_intent.append(true_intent)
        y_pred_intent.append(pred_intent)

        y_true_decision.append(true_decision)
        y_pred_decision.append(pred_decision)

        # ROUGE-L overlap
        rouge_res = scorer.score(ref_reply, pred_reply)
        rouge_l_scores.append(rouge_res['rougeL'].fmeasure)

        # LLM-as-Judge Rubric
        eval_metrics = judge.evaluate_reply(
            customer_query=tweet_text,
            generated_reply=pred_reply,
            reference_reply=ref_reply,
            true_decision=true_decision,
            pred_decision=pred_decision
        )

        grounding_scores.append(eval_metrics["grounding_score"])
        tone_scores.append(eval_metrics["tone_score"])
        composite_scores.append(eval_metrics["composite_score"])

    # Calculate aggregate classification & decision metrics
    intent_acc = accuracy_score(y_true_intent, y_pred_intent)
    
    # Escalation binary metrics ("ESCALATE" = 1, "AUTO_HANDLE" = 0)
    b_true = [1 if d == "ESCALATE" else 0 for d in y_true_decision]
    b_pred = [1 if d == "ESCALATE" else 0 for d in y_pred_decision]

    p, r, f1, _ = precision_recall_fscore_support(b_true, b_pred, average='binary', zero_division=0)

    return {
        "system_name": system_name,
        "intent_accuracy": round(float(intent_acc) * 100.0, 2),
        "escalation_precision": round(float(p) * 100.0, 2),
        "escalation_recall": round(float(r) * 100.0, 2),
        "escalation_f1": round(float(f1) * 100.0, 2),
        "avg_grounding_score": round(float(sum(grounding_scores) / len(grounding_scores)), 2),
        "avg_tone_score": round(float(sum(tone_scores) / len(tone_scores)), 2),
        "avg_composite_judge_score": round(float(sum(composite_scores) / len(composite_scores)), 2),
        "avg_rouge_l": round(float(sum(rouge_l_scores) / len(rouge_l_scores)), 4),
        "avg_latency_ms": round(float(sum(latencies_ms) / len(latencies_ms)), 2)
    }


def run_full_evaluation():
    """
    Executes the entire evaluation suite comparing Proposed LangGraph Agent vs Baselines.
    """
    if not GOLDEN_SET_PATH.exists():
        raise FileNotFoundError(f"Golden set file not found at {GOLDEN_SET_PATH}")

    with open(GOLDEN_SET_PATH, "r", encoding="utf-8") as f:
        golden_data = json.load(f)

    judge = LLMAsJudgeRubric()

    b0 = Baseline0Trivial()
    b1 = Baseline1SimpleRAG()

    print(f"Loaded {len(golden_data)} golden examples. Running evaluation suite...")

    res_b0 = evaluate_system("Baseline 0 (Trivial)", b0.process, golden_data, judge)
    print("Baseline 0 Complete.")

    res_b1 = evaluate_system("Baseline 1 (Simple RAG)", b1.process, golden_data, judge)
    print("Baseline 1 Complete.")

    res_proposed = evaluate_system("Proposed System (LangGraph + RAG)", run_agent_pipeline, golden_data, judge)
    print("Proposed System Complete.")

    # Human agreement
    human_calibration = calculate_human_judge_agreement()

    summary = {
        "golden_set_size": len(golden_data),
        "results": [res_b0, res_b1, res_proposed],
        "human_judge_agreement": human_calibration
    }

    # Save summary report artifact
    eval_results_path = Path(__file__).parent / "evaluation_results.json"
    with open(eval_results_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n=======================================================")
    print("               HEADLINE EVALUATION RESULTS            ")
    print("=======================================================")
    print(f"{'Metric':<30} | {'Baseline 0':<12} | {'Baseline 1':<12} | {'Proposed Agent':<15}")
    print("-" * 75)
    print(f"{'Intent Accuracy (%)':<30} | {res_b0['intent_accuracy']:<12} | {res_b1['intent_accuracy']:<12} | {res_proposed['intent_accuracy']:<15}")
    print(f"{'Escalation Precision (%)':<30} | {res_b0['escalation_precision']:<12} | {res_b1['escalation_precision']:<12} | {res_proposed['escalation_precision']:<15}")
    print(f"{'Escalation Recall (%)':<30} | {res_b0['escalation_recall']:<12} | {res_b1['escalation_recall']:<12} | {res_proposed['escalation_recall']:<15}")
    print(f"{'Escalation F1-Score (%)':<30} | {res_b0['escalation_f1']:<12} | {res_b1['escalation_f1']:<12} | {res_proposed['escalation_f1']:<15}")
    print(f"{'Grounding Score (1-5)':<30} | {res_b0['avg_grounding_score']:<12} | {res_b1['avg_grounding_score']:<12} | {res_proposed['avg_grounding_score']:<15}")
    print(f"{'Composite Judge Score (1-5)':<30} | {res_b0['avg_composite_judge_score']:<12} | {res_b1['avg_composite_judge_score']:<12} | {res_proposed['avg_composite_judge_score']:<15}")
    print(f"{'ROUGE-L Score':<30} | {res_b0['avg_rouge_l']:<12} | {res_b1['avg_rouge_l']:<12} | {res_proposed['avg_rouge_l']:<15}")
    print(f"{'Avg Latency (ms)':<30} | {res_b0['avg_latency_ms']:<12} | {res_b1['avg_latency_ms']:<12} | {res_proposed['avg_latency_ms']:<15}")
    print("=======================================================")
    print(f"Human-Judge Calibration (Cohen's Kappa): {human_calibration['cohens_kappa']} ({human_calibration['percentage_agreement']}% agreement)")
    print("=======================================================\n")

    return summary


if __name__ == "__main__":
    run_full_evaluation()



if __name__ == "__main__":
    run_full_evaluation()
