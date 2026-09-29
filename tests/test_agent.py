"""
Unit and Integration Tests for Insurance Risk Profile Summarizer.
"""

import unittest
import os
import sys
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from agent.risk_agent import RiskAgent
from agent.preprocessor import Preprocessor
from agent.scorer import RiskScorer
from agent.synthesizer import RiskSynthesizer


class TestRiskProfileSummarizer(unittest.TestCase):

    def setUp(self):
        self.agent = RiskAgent()
        self.preprocessor = Preprocessor()
        self.scorer = RiskScorer()
        self.synthesizer = RiskSynthesizer()

        # Sample valid profile
        self.sample_profile = {
            "customer_id": "TEST-CUST-001",
            "policy_type": "Auto",
            "demographics": {
                "age": 38,
                "occupation_category": "Professional / Desk",
                "location_risk_tier": "Low",
                "credit_tier": "Excellent (750+)",
                "customer_tenure_years": 5.0
            },
            "policy_details": {
                "coverage_amount": 200000,
                "deductible": 1000,
                "policy_term_months": 12,
                "existing_premium": 900
            },
            "claim_history": {
                "total_claims": 0,
                "claims_last_3_years": 0,
                "total_incurred_amount": 0,
                "at_fault_claims_count": 0,
                "claims": []
            },
            "risk_factors": {
                "telematics_score": 92,
                "traffic_violations_last_3_years": 0,
                "vehicle_annual_mileage": 10000
            }
        }

    def test_preprocessor_missing_field_raises(self):
        invalid_data = {"customer_id": "TEST"}
        with self.assertRaises(ValueError):
            self.preprocessor.validate_and_preprocess(invalid_data)

    def test_preprocessor_pii_sanitization(self):
        data_with_pii = dict(self.sample_profile)
        data_with_pii["demographics"]["customer_ssn"] = "123-45-6789"
        data_with_pii["contact_email"] = "applicant@confidential-real-email.com"

        normalized, warnings = self.preprocessor.validate_and_preprocess(data_with_pii)
        # Verify PII fields were stripped
        self.assertNotIn("contact_email", normalized)
        self.assertTrue(any("PII Flag" in w for w in warnings))

    def test_preprocessor_derived_metrics(self):
        normalized, _ = self.preprocessor.validate_and_preprocess(self.sample_profile)
        derived = normalized.get("derived_metrics", {})
        self.assertIn("loss_to_coverage_ratio", derived)
        self.assertIn("claim_frequency_rate", derived)
        self.assertEqual(derived["loss_to_coverage_ratio"], 0.0)

    def test_low_risk_scoring(self):
        normalized, _ = self.preprocessor.validate_and_preprocess(self.sample_profile)
        evaluation = self.scorer.evaluate_risk(normalized)
        self.assertLessEqual(evaluation["risk_score"], 25.0)
        self.assertEqual(evaluation["risk_tier"], "Low / Preferred")
        self.assertIn("Approve", evaluation["underwriting_decision"])
        self.assertGreater(len(evaluation["mitigating_factors"]), 0)

    def test_high_risk_scoring(self):
        high_risk_profile = dict(self.sample_profile)
        high_risk_profile["claim_history"] = {
            "total_claims": 4,
            "claims_last_3_years": 4,
            "total_incurred_amount": 120000,
            "at_fault_claims_count": 3,
            "claims": []
        }
        high_risk_profile["risk_factors"] = {
            "telematics_score": 45,
            "traffic_violations_last_3_years": 3,
            "vehicle_annual_mileage": 25000
        }
        normalized, _ = self.preprocessor.validate_and_preprocess(high_risk_profile)
        evaluation = self.scorer.evaluate_risk(normalized)
        self.assertGreaterEqual(evaluation["risk_score"], 75.0)
        self.assertEqual(evaluation["risk_tier"], "High / Critical Risk")

    def test_synthesizer_structure(self):
        normalized, _ = self.preprocessor.validate_and_preprocess(self.sample_profile)
        evaluation = self.scorer.evaluate_risk(normalized)
        synthesis = self.synthesizer.synthesize(normalized, evaluation)

        self.assertIn("executive_summary", synthesis)
        self.assertIn("detailed_narrative", synthesis)
        self.assertGreater(len(synthesis["executive_summary"]), 20)
        self.assertIn("### 1. Exposure & Demographics Analysis", synthesis["detailed_narrative"])

    def test_agent_end_to_end_and_speed_sla(self):
        output = self.agent.process(self.sample_profile)
        self.assertEqual(output["status"], "success")
        self.assertTrue(output["metadata"]["meets_speed_sla"])
        self.assertLess(output["metadata"]["processing_time_seconds"], 20.0)
        self.assertTrue(output["metadata"]["guardrail_status"]["all_passed"])
        self.assertIn("risk_assessment", output)
        self.assertIn("summary", output)


if __name__ == "__main__":
    unittest.main()
