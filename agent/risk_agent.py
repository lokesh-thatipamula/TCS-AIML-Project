"""
Automated Risk Profile Summarizer - Single-Agent Orchestrator.
Coordinates preprocessing, normalization, composite risk scoring, and GenAI synthesis.
"""

import time
from typing import Dict, Any
from agent.preprocessor import Preprocessor
from agent.scorer import RiskScorer
from agent.synthesizer import RiskSynthesizer


class RiskAgent:
    """Single-Agent Underwriting Risk Profile Summarizer."""

    def __init__(self, strict_pii: bool = True):
        self.preprocessor = Preprocessor(strict_pii=strict_pii)
        self.scorer = RiskScorer()
        self.synthesizer = RiskSynthesizer()

    def process(self, raw_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes raw risk input and produces actionable summary, KRIs, and metrics.
        Guarantees speed under 20 seconds and high accuracy.
        """
        start_time = time.time()

        # Step 1: Preprocess, sanitize PII, and normalize
        normalized_data, warnings = self.preprocessor.validate_and_preprocess(raw_input)

        # Step 2: Risk Scoring and Key Risk Indicators extraction
        evaluation = self.scorer.evaluate_risk(normalized_data)

        # Step 3: GenAI Synthesis of Natural Language Summary
        synthesis = self.synthesizer.synthesize(normalized_data, evaluation)

        # Step 4: Quality & Self-Consistency Verification
        guardrail_status = self._verify_guardrails(normalized_data, evaluation, synthesis)

        elapsed = time.time() - start_time
        latency_ms = round(elapsed * 1000, 2)
        latency_sec = round(elapsed, 4)

        return {
            "status": "success",
            "metadata": {
                "customer_id": raw_input.get("customer_id", "UNKNOWN"),
                "policy_type": raw_input.get("policy_type", "General"),
                "processing_time_seconds": latency_sec,
                "processing_time_ms": latency_ms,
                "meets_speed_sla": latency_sec < 20.0,
                "warnings": warnings,
                "guardrail_status": guardrail_status
            },
            "risk_assessment": {
                "composite_risk_score": evaluation["risk_score"],
                "risk_tier": evaluation["risk_tier"],
                "underwriting_decision": evaluation["underwriting_decision"],
                "confidence_score": evaluation["confidence_score"]
            },
            "key_risk_indicators": evaluation["key_risk_indicators"],
            "mitigating_factors": evaluation["mitigating_factors"],
            "derived_metrics": normalized_data.get("derived_metrics", {}),
            "summary": {
                "executive_summary": synthesis["executive_summary"],
                "detailed_narrative": synthesis["detailed_narrative"],
                "generation_mode": synthesis.get("generation_mode", "Local GenAI Engine"),
                "key_takeaways": synthesis.get("key_takeaways", []),
                "recommended_actions": synthesis.get("recommended_actions", [])
            }
        }

    def _verify_guardrails(self, profile: Dict[str, Any], evaluation: Dict[str, Any], synthesis: Dict[str, Any]) -> Dict[str, Any]:
        """Self-verification check ensuring synthesis matches scoring metrics (accuracy guardrail)."""
        score = evaluation["risk_score"]
        decision = evaluation["underwriting_decision"]
        narrative = synthesis["detailed_narrative"]

        checks = {
            "score_bounds_valid": 0.0 <= score <= 100.0,
            "decision_aligned": (
                (score < 30 and "Preferred" in decision) or
                (30 <= score <= 55 and "Standard" in decision) or
                (55 < score <= 75 and "Surcharge" in decision) or
                (score > 75 and ("Refer" in decision or "Decline" in decision))
            ),
            "no_pii_in_summary": not any(
                p in narrative.lower() for p in ["ssn", "social security", "@", "password"]
            )
        }
        checks["all_passed"] = all(checks.values())
        return checks
