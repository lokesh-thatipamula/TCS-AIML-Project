"""
Data Preprocessor & Normalizer for Insurance Risk Profiles.
Handles validation, synthetic data compliance (PII checks), and feature normalization.
"""

import re
from typing import Dict, Any, Tuple, List


class Preprocessor:
    """Preprocesses and normalizes insurance customer risk profiles."""

    PII_PATTERNS = {
        "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
        "phone": re.compile(r"\b(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}\b"),
        "credit_card": re.compile(r"\b(?:\d{4}[ -]?){3}\d{4}\b")
    }

    SUSPICIOUS_PII_KEYS = {"name", "full_name", "first_name", "last_name", "ssn", "phone", "email", "address", "street"}

    def __init__(self, strict_pii: bool = True):
        self.strict_pii = strict_pii

    def validate_and_preprocess(self, raw_data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """
        Validates input structure, enforces synthetic anonymity, and calculates normalized metrics.
        Returns: (normalized_data, warnings_list)
        """
        warnings = []
        if not isinstance(raw_data, dict):
            raise ValueError("Input data must be a JSON object.")

        # 1. Structural requirements check
        required_roots = ["customer_id", "policy_type", "demographics", "policy_details", "claim_history", "risk_factors"]
        for key in required_roots:
            if key not in raw_data:
                raise ValueError(f"Missing mandatory section in risk profile: '{key}'")

        # 2. PII / Synthetic data compliance check
        sanitized_data, pii_warnings = self._check_and_sanitize_pii(raw_data)
        warnings.extend(pii_warnings)

        # 3. Normalization and derived metric calculations
        normalized = self._normalize_metrics(sanitized_data)

        return normalized, warnings

    def _check_and_sanitize_pii(self, data: Any) -> Tuple[Any, List[str]]:
        """Detects and strips any inadvertent personal data to guarantee synthetic compliance."""
        warnings = []

        def recurse(node, path=""):
            if isinstance(node, dict):
                cleaned = {}
                for k, v in node.items():
                    current_path = f"{path}.{k}" if path else k
                    if any(sub in k.lower() for sub in self.SUSPICIOUS_PII_KEYS):
                        warnings.append(f"PII Flag: Key '{current_path}' removed to maintain synthetic anonymization.")
                        continue
                    cleaned[k] = recurse(v, current_path)
                return cleaned
            elif isinstance(node, list):
                return [recurse(elem, f"{path}[{idx}]") for idx, elem in enumerate(node)]
            elif isinstance(node, str):
                # Pattern scanning
                for pii_type, regex in self.PII_PATTERNS.items():
                    if regex.search(node):
                        warnings.append(f"PII Flag: Potential {pii_type.upper()} pattern detected at '{path}'. Anonymizing.")
                        node = regex.sub("[ANONYMIZED]", node)
                return node
            return node

        sanitized = recurse(data)
        return sanitized, warnings

    def _normalize_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates normalized ratios and consolidated indicators for downstream modeling."""
        norm = dict(data)
        demographics = norm.get("demographics", {})
        policy = norm.get("policy_details", {})
        claims = norm.get("claim_history", {})
        risks = norm.get("risk_factors", {})
        financials = norm.get("financial_indicators", {})

        coverage_amount = float(policy.get("coverage_amount", 100000) or 100000)
        total_incurred = float(claims.get("total_incurred_amount", 0) or 0)
        claims_3y = int(claims.get("claims_last_3_years", 0) or 0)
        total_claims = int(claims.get("total_claims", claims_3y) or claims_3y)
        at_fault_count = int(claims.get("at_fault_claims_count", 0) or 0)

        # Normalized loss ratio relative to limit
        loss_to_coverage_ratio = round(min(total_incurred / coverage_amount, 5.0), 4)

        # Claim frequency per year (3-year window)
        claim_frequency_rate = round(claims_3y / 3.0, 2)

        # At-fault ratio
        at_fault_ratio = round(at_fault_count / max(total_claims, 1), 2)

        # Credit tier score mapping (0 to 100 scale, higher is better credit / lower risk)
        credit_tier = str(demographics.get("credit_tier", "Good (700-749)"))
        credit_scores = {
            "Excellent (750+)": 90,
            "Good (700-749)": 75,
            "Fair (650-699)": 50,
            "Poor (<650)": 25
        }
        credit_score_normalized = credit_scores.get(credit_tier, 65)

        # Age group risk categorization
        age = demographics.get("age", 40)
        if age < 25:
            age_risk_tag = "Younger / Inexperienced demographic"
        elif age > 75:
            age_risk_tag = "Senior demographic"
        else:
            age_risk_tag = "Standard mature demographic"

        # Derived consolidated indicators
        norm["derived_metrics"] = {
            "loss_to_coverage_ratio": loss_to_coverage_ratio,
            "claim_frequency_rate": claim_frequency_rate,
            "at_fault_ratio": at_fault_ratio,
            "credit_score_normalized": credit_score_normalized,
            "age_risk_tag": age_risk_tag,
            "high_frequency_flag": claims_3y >= 2,
            "severe_loss_flag": loss_to_coverage_ratio > 0.40,
            "adverse_credit_flag": credit_score_normalized <= 50
        }

        return norm
