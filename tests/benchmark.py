"""
Benchmark Evaluator for Insurance Risk Profile Summarizer.
Measures:
1. Underwriting Decision & KRI Extraction Accuracy (Success target: >= 85%)
2. Processing Latency & Speed SLA (Success target: < 20.0 seconds)
"""

import json
import os
import sys
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from typing import Dict, Any, List
from agent.risk_agent import RiskAgent


def run_benchmark() -> Dict[str, Any]:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)

    profiles_path = os.path.join(project_root, "data", "synthetic_profiles.json")
    ground_truth_path = os.path.join(project_root, "data", "ground_truth_eval.json")

    with open(profiles_path, "r", encoding="utf-8") as f:
        profiles = json.load(f)
    with open(ground_truth_path, "r", encoding="utf-8") as f:
        ground_truths = {gt["customer_id"]: gt for gt in json.load(f)}

    agent = RiskAgent()

    results: List[Dict[str, Any]] = []
    total_latency = 0.0
    passed_criteria_count = 0
    total_criteria_count = 0

    for profile in profiles:
        cust_id = profile["customer_id"]
        gt = ground_truths.get(cust_id)
        if not gt:
            continue

        start_t = time.time()
        output = agent.process(profile)
        elapsed = time.time() - start_t
        total_latency += elapsed

        score = output["risk_assessment"]["composite_risk_score"]
        tier = output["risk_assessment"]["risk_tier"]
        decision = output["risk_assessment"]["underwriting_decision"]
        kris = output["key_risk_indicators"]
        mitigating = output["mitigating_factors"]
        kri_text = " ".join([k["indicator"] + " " + k.get("detail", "") for k in kris])
        mit_text = " ".join(mitigating)

        # Accuracy checks
        # 1. Tier Match
        exp_tier = gt["expected_risk_tier"]
        if isinstance(exp_tier, list):
            tier_passed = tier in exp_tier
        else:
            tier_passed = (tier == exp_tier)
        total_criteria_count += 1
        if tier_passed:
            passed_criteria_count += 1

        # 2. Decision Keywords Match
        decision_passed = any(kw.lower() in decision.lower() for kw in gt["expected_decision_contains"])
        total_criteria_count += 1
        if decision_passed:
            passed_criteria_count += 1

        # 3. Score Range Match
        s_min, s_max = gt["score_range"]
        score_passed = (s_min <= score <= s_max)
        total_criteria_count += 1
        if score_passed:
            passed_criteria_count += 1

        # 4. KRI Keywords Match (if specified)
        kri_passed = True
        if "expected_kri_keywords" in gt:
            for kw in gt["expected_kri_keywords"]:
                total_criteria_count += 1
                if kw.lower() in kri_text.lower():
                    passed_criteria_count += 1
                else:
                    kri_passed = False

        # 5. Speed SLA check (< 20 seconds)
        speed_passed = elapsed < 20.0

        profile_accuracy = round(
            (int(tier_passed) + int(decision_passed) + int(score_passed) + int(kri_passed)) / 4.0 * 100, 1
        )

        results.append({
            "customer_id": cust_id,
            "policy_type": profile.get("policy_type"),
            "risk_score": score,
            "risk_tier": tier,
            "underwriting_decision": decision,
            "latency_seconds": round(elapsed, 4),
            "speed_sla_met": speed_passed,
            "profile_accuracy_pct": profile_accuracy,
            "tier_match": tier_passed,
            "decision_match": decision_passed,
            "score_match": score_passed
        })

    overall_accuracy = round((passed_criteria_count / max(total_criteria_count, 1)) * 100, 2)
    avg_latency = round(total_latency / max(len(results), 1), 4)
    max_latency = round(max([r["latency_seconds"] for r in results]), 4) if results else 0.0

    summary = {
        "total_profiles_evaluated": len(results),
        "overall_accuracy_pct": overall_accuracy,
        "target_accuracy_pct": 85.0,
        "accuracy_target_achieved": overall_accuracy >= 85.0,
        "average_generation_latency_seconds": avg_latency,
        "maximum_generation_latency_seconds": max_latency,
        "target_max_latency_seconds": 20.0,
        "speed_sla_achieved": max_latency < 20.0,
        "results": results
    }

    return summary


if __name__ == "__main__":
    benchmark_report = run_benchmark()
    print("=" * 60)
    print(" INSURANCE RISK PROFILE SUMMARIZER - BENCHMARK REPORT")
    print("=" * 60)
    print(f"Profiles Tested      : {benchmark_report['total_profiles_evaluated']}")
    print(f"Overall Accuracy     : {benchmark_report['overall_accuracy_pct']}%  (Target: >= 85.0%) -> {'[PASS]' if benchmark_report['accuracy_target_achieved'] else '[FAIL]'}")
    print(f"Average Latency      : {benchmark_report['average_generation_latency_seconds']}s (Target: < 20.0s) -> {'[PASS]' if benchmark_report['speed_sla_achieved'] else '[FAIL]'}")
    print(f"Maximum Latency      : {benchmark_report['maximum_generation_latency_seconds']}s")
    print("=" * 60)
    for res in benchmark_report["results"]:
        print(f" - {res['customer_id']} ({res['policy_type']}): Score={res['risk_score']} | Tier={res['risk_tier']} | Acc={res['profile_accuracy_pct']}% | Latency={res['latency_seconds']}s")
    print("=" * 60)
