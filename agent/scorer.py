"""
Composite Risk Scoring and Key Risk Indicators (KRI) Engine.
Evaluates multi-factor insurance risk across demographics, claims, and domain factors.
"""

from typing import Dict, Any, List


class RiskScorer:
    """Calculates actuarial risk score, extracts KRIs, and formulates underwriting recommendations."""

    def evaluate_risk(self, normalized_data: Dict[str, Any]) -> Dict[str, Any]:
        policy_type = normalized_data.get("policy_type", "Auto")
        demographics = normalized_data.get("demographics", {})
        policy = normalized_data.get("policy_details", {})
        claims = normalized_data.get("claim_history", {})
        risks = normalized_data.get("risk_factors", {})
        derived = normalized_data.get("derived_metrics", {})

        base_score = 20.0  # Base standard score
        kris: List[Dict[str, str]] = []
        mitigating: List[str] = []
        conditions: List[str] = []

        # --- Factor 1: Claims & Loss History (Weight: ~35%) ---
        claims_3y = claims.get("claims_last_3_years", 0)
        total_incurred = claims.get("total_incurred_amount", 0)
        at_fault = claims.get("at_fault_claims_count", 0)
        loss_ratio = derived.get("loss_to_coverage_ratio", 0.0)

        if claims_3y >= 3 or at_fault >= 2:
            base_score += 30.0
            kris.append({
                "category": "Claim Frequency",
                "severity": "CRITICAL",
                "indicator": f"High Claim Velocity ({claims_3y} claims in 3 yrs, {at_fault} at-fault)",
                "detail": f"Cumulative incurred losses of ${total_incurred:,.2f} indicate sustained loss frequency."
            })
        elif claims_3y == 2 or at_fault == 1:
            base_score += 18.0
            kris.append({
                "category": "Claim Frequency",
                "severity": "HIGH",
                "indicator": f"Elevated Claim Frequency ({claims_3y} claims in 3 yrs)",
                "detail": f"Historical payouts totaling ${total_incurred:,.2f} require rate scrutiny."
            })
        elif claims_3y == 1:
            base_score += 8.0
            kris.append({
                "category": "Claim Frequency",
                "severity": "MEDIUM",
                "indicator": "Single Prior Claim Recorded",
                "detail": f"1 claim in past 3 years (${total_incurred:,.2f})."
            })
        else:
            base_score -= 8.0
            mitigating.append("Clean Claims Record: Zero claims filed over the past 36 months.")

        if loss_ratio > 0.50:
            base_score += 15.0
            kris.append({
                "category": "Loss Severity",
                "severity": "HIGH",
                "indicator": f"High Loss-to-Coverage Ratio ({loss_ratio*100:.1f}%)",
                "detail": f"Incurred claims (${total_incurred:,.0f}) exceed 50% of policy limit (${policy.get('coverage_amount', 0):,.0f})."
            })

        # --- Factor 2: Demographics & Financial Stability (Weight: ~20%) ---
        age = demographics.get("age", 40)
        credit_tier = demographics.get("credit_tier", "Good (700-749)")
        tenure = demographics.get("customer_tenure_years", 0)
        loc_tier = demographics.get("location_risk_tier", "Moderate")

        if age < 25:
            base_score += 10.0
            kris.append({
                "category": "Demographics",
                "severity": "MEDIUM" if policy_type == "Auto" else "LOW",
                "indicator": f"Youthful / Inexperienced Applicant (Age {age})",
                "detail": "Statistical loss frequency is historically higher for youthful demographics."
            })
        elif age >= 75:
            base_score += 6.0

        if "Poor" in credit_tier:
            base_score += 14.0
            kris.append({
                "category": "Credit Risk",
                "severity": "HIGH",
                "indicator": "Subprime Credit Classification",
                "detail": "Credit rating tier <650 correlates statistically with higher loss propensity."
            })
        elif "Fair" in credit_tier:
            base_score += 6.0
            kris.append({
                "category": "Credit Risk",
                "severity": "MEDIUM",
                "indicator": "Fair Credit Rating",
                "detail": "Credit tier in 650-699 band."
            })
        elif "Excellent" in credit_tier:
            base_score -= 6.0
            mitigating.append("Prime Credit Profile (750+ score) demonstrates financial stability.")

        if loc_tier in ["High", "Very High"]:
            base_score += 10.0
            kris.append({
                "category": "Geographic Exposure",
                "severity": "MEDIUM" if loc_tier == "High" else "HIGH",
                "indicator": f"{loc_tier} Risk Territory Assignment",
                "detail": "Geographic zone displays elevated hazard, catastrophe, or theft indices."
            })
        elif loc_tier == "Low":
            base_score -= 4.0
            mitigating.append("Favorable Low-Risk Territory rating.")

        if tenure >= 5:
            base_score -= 6.0
            mitigating.append(f"Established Customer Loyalty: {tenure:.1f} years of verified insurance tenure.")

        # --- Factor 3: Domain-Specific Risk Factors (Weight: ~45%) ---
        if policy_type == "Auto":
            telematics = risks.get("telematics_score")
            violations = risks.get("traffic_violations_last_3_years", 0)
            mileage = risks.get("vehicle_annual_mileage", 12000)

            if violations >= 2:
                base_score += 20.0
                kris.append({
                    "category": "Driving Record",
                    "severity": "CRITICAL",
                    "indicator": f"Adverse MVR ({violations} moving violations)",
                    "detail": "Multiple traffic citations indicate persistent driving infractions."
                })
            elif violations == 1:
                base_score += 10.0
                kris.append({
                    "category": "Driving Record",
                    "severity": "MEDIUM",
                    "indicator": "Single Moving Violation on MVR",
                    "detail": "1 moving violation documented in the trailing 3 years."
                })
            else:
                mitigating.append("Spotless Motor Vehicle Record (MVR): Zero moving violations.")

            if telematics is not None:
                if telematics >= 85:
                    base_score -= 10.0
                    mitigating.append(f"Exceptional Telematics Driving Score ({telematics}/100) confirms defensive driving habits.")
                elif telematics < 60:
                    base_score += 15.0
                    kris.append({
                        "category": "Telematics",
                        "severity": "HIGH",
                        "indicator": f"Subpar Telematics Driving Score ({telematics}/100)",
                        "detail": "High frequency of harsh braking, rapid acceleration, or late-night driving."
                    })

            if mileage > 20000:
                base_score += 8.0
                kris.append({
                    "category": "Exposure",
                    "severity": "LOW",
                    "indicator": f"High Annual Road Exposure ({mileage:,.0f} miles/yr)",
                    "detail": "Substantially above the national commuter average of 12,000 miles."
                })

        elif policy_type == "Property":
            prop_age = risks.get("property_age_years", 10)
            roof = risks.get("roof_condition_score", 8.0)
            flood = risks.get("flood_zone", False)
            wildfire = risks.get("wildfire_risk_score", "Low")
            security = risks.get("security_system_installed", False)

            if flood:
                base_score += 22.0
                kris.append({
                    "category": "Flood Exposure",
                    "severity": "CRITICAL",
                    "indicator": "Special Flood Hazard Area (SFHA) Designation",
                    "detail": "Property is situated in a high-risk FEMA 100-year flood plain."
                })
                conditions.append("Mandate separate NFIP/Flood policy or sign Flood Exclusion Endorsement.")

            if wildfire in ["High", "Extreme"]:
                base_score += 18.0
                kris.append({
                    "category": "Catastrophe Risk",
                    "severity": "CRITICAL" if wildfire == "Extreme" else "HIGH",
                    "indicator": f"{wildfire} Wildfire Hazard Index",
                    "detail": "Severe vegetative fuel and topography elevate brushfire vulnerability."
                })
                conditions.append("Require 100ft defensible space clearance inspection certificate.")

            if roof <= 4.0 or prop_age > 40:
                base_score += 12.0
                kris.append({
                    "category": "Structural Wear",
                    "severity": "HIGH",
                    "indicator": f"Aging Roof / Structure (Age: {prop_age} yrs, Condition: {roof}/10)",
                    "detail": "Heightened susceptibility to wind, hail, and interior water infiltration."
                })
                conditions.append("Require ACV (Actual Cash Value) roof settlement rather than Replacement Cost.")

            if security:
                base_score -= 6.0
                mitigating.append("Monitored 24/7 burglar and fire central alarm system active.")

        elif policy_type in ["Health", "Life"]:
            smoker = risks.get("smoker_status", False)
            bmi = risks.get("bmi", 24.0)
            pre_existing = risks.get("pre_existing_conditions", [])

            if smoker:
                base_score += 25.0
                kris.append({
                    "category": "Lifestyle Risk",
                    "severity": "CRITICAL" if policy_type == "Life" else "HIGH",
                    "indicator": "Active Tobacco / Nicotine User",
                    "detail": "Smoking substantially accelerates mortality and morbidity risk multiples."
                })
                conditions.append("Apply standard tobacco premium loading (typically +50% to +100%).")

            if bmi >= 35.0:
                base_score += 14.0
                kris.append({
                    "category": "Clinical Indicator",
                    "severity": "HIGH",
                    "indicator": f"Severe / Class II Obesity (BMI: {bmi})",
                    "detail": "Elevates likelihood of cardiovascular, metabolic, and orthopedic complications."
                })
            elif bmi < 18.5:
                base_score += 8.0
                kris.append({
                    "category": "Clinical Indicator",
                    "severity": "MEDIUM",
                    "indicator": f"Underweight Metric (BMI: {bmi})",
                    "detail": "Underweight classification warrants medical history review."
                })
            elif 18.5 <= bmi <= 26.0:
                mitigating.append(f"Ideal Body Mass Index ({bmi}) within optimal healthy clinical range.")

            if len(pre_existing) >= 2:
                base_score += 20.0
                kris.append({
                    "category": "Chronic Conditions",
                    "severity": "HIGH",
                    "indicator": f"Multiple Chronic Diagnoses: {', '.join(pre_existing)}",
                    "detail": "Comorbid health conditions require underwriting review."
                })
                conditions.append(f"Attach specific pre-existing condition exclusions for {', '.join(pre_existing[:2])}.")
            elif len(pre_existing) == 1:
                base_score += 10.0
                kris.append({
                    "category": "Chronic Conditions",
                    "severity": "MEDIUM",
                    "indicator": f"Diagnosed Medical Condition: {pre_existing[0]}",
                    "detail": "Under maintenance therapy."
                })

        # Final Score Normalization (Clamp 5 - 98)
        final_risk_score = round(max(5.0, min(98.0, base_score)), 1)

        # Categorization & Underwriting Decision Logic
        if final_risk_score <= 25.0:
            risk_tier = "Low / Preferred"
            decision = "Approve - Preferred Rates"
            if not conditions:
                conditions.append("Eligible for maximum tier discount and preferred pricing.")
        elif final_risk_score <= 55.0:
            risk_tier = "Moderate / Standard"
            decision = "Approve - Standard Rates"
            if not conditions:
                conditions.append("Standard deductible ($1,000) and baseline rating guidelines apply.")
        elif final_risk_score <= 75.0:
            risk_tier = "Elevated / Substandard"
            decision = "Approve with Surcharge / Conditions"
            if not conditions:
                conditions.append("Apply 15% to 25% underwriting rate surcharge.")
                conditions.append("Adjust deductible upwards to mitigate minor claim frequency.")
        else:
            risk_tier = "High / Critical Risk"
            # If critical flags are severe
            critical_kris = [k for k in kris if k["severity"] == "CRITICAL"]
            if len(critical_kris) >= 2 or final_risk_score >= 85:
                decision = "Decline Coverage"
                conditions.append("Unacceptable loss expectancy outside acceptable reinsurance treaty parameters.")
            else:
                decision = "Refer to Senior Underwriter"
                conditions.append("Mandate manual underwriting review and secondary inspection audit.")

        confidence_score = 0.94 if len(kris) + len(mitigating) >= 4 else 0.88

        return {
            "risk_score": final_risk_score,
            "risk_tier": risk_tier,
            "underwriting_decision": decision,
            "confidence_score": confidence_score,
            "key_risk_indicators": kris,
            "mitigating_factors": mitigating,
            "recommended_conditions": conditions
        }
