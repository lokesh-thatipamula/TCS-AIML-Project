# Data Schema & Dictionary: Automated Risk Profile Summarizer

## Overview
This document specifies the standardized data architecture for the **Automated Risk Profile Summarizer**. 
To strictly satisfy compliance and data protection standards ("No personal data involved. Consider using synthetic or anonymized data where appropriate"), the schema excludes all Personally Identifiable Information (PII) and relies on synthetic domain-specific risk structures.

---

## 1. Schema Specifications

All inputs must adhere to the standardized JSON schema defined in [`data/schema.json`](file:///Users/lokeshthatipamula/Documents/TCS-AIML-Project/data/schema.json).

```json
{
  "customer_id": "CUST-AUTO-101",
  "policy_type": "Auto",
  "demographics": {
    "age": 42,
    "occupation_category": "Professional / Desk",
    "location_risk_tier": "Low",
    "credit_tier": "Excellent (750+)",
    "customer_tenure_years": 7.5
  },
  "policy_details": {
    "coverage_amount": 250000,
    "deductible": 1000,
    "policy_term_months": 12,
    "existing_premium": 1150
  },
  "claim_history": {
    "total_claims": 0,
    "claims_last_3_years": 0,
    "total_incurred_amount": 0,
    "at_fault_claims_count": 0,
    "open_claims_count": 0,
    "claims": []
  },
  "risk_factors": {
    "telematics_score": 94,
    "traffic_violations_last_3_years": 0,
    "vehicle_annual_mileage": 9500
  },
  "financial_indicators": {
    "debt_to_income_ratio": 0.22,
    "payment_delinquencies_count": 0,
    "annual_income_bracket": "$75,000 - $150,000"
  }
}
```

---

## 2. Field Dictionary & Type Rules

### Root Elements
| Field | Type | Description | Allowed Values / Constraints |
| :--- | :--- | :--- | :--- |
| `customer_id` | String | Synthetic unique identifier | Pattern: `^[A-Z0-9_-]+$` |
| `policy_type` | String | Insurance line of business | `"Auto"`, `"Property"`, `"Health"`, `"Life"` |
| `demographics` | Object | Anonymized applicant metadata | Mandatory |
| `policy_details` | Object | Policy limits & deductibles | Mandatory |
| `claim_history` | Object | Historical claims record | Mandatory |
| `risk_factors` | Object | Line-specific hazard indicators | Mandatory |
| `financial_indicators`| Object | Financial stability metrics | Optional |

### Demographics Section
| Field | Type | Description |
| :--- | :--- | :--- |
| `age` | Integer | Insured age (18 - 100) |
| `occupation_category`| String | `"Professional / Desk"`, `"Healthcare"`, `"Trades / Manual Labor"`, `"Commercial Driving / Transport"`, `"High Risk / Hazardous"`, `"Retired"`, `"Student"` |
| `location_risk_tier` | String | Territory hazard tier: `"Low"`, `"Moderate"`, `"High"`, `"Very High"` |
| `credit_tier` | String | Insurance score: `"Excellent (750+)"`, `"Good (700-749)"`, `"Fair (650-699)"`, `"Poor (<650)"` |
| `customer_tenure_years`| Float | Duration of coverage with carrier (years) |

### Claim History Section
| Field | Type | Description |
| :--- | :--- | :--- |
| `total_claims` | Integer | Lifetime claims filed |
| `claims_last_3_years`| Integer | Claims filed in the last 36 months (primary frequency driver) |
| `total_incurred_amount`| Float | Cumulative historical dollar payout ($) |
| `at_fault_claims_count`| Integer | Count of incidents where insured bore liability |
| `claims` | Array | Itemized incident objects with `incident_date`, `claim_type`, `amount_paid`, `at_fault`, `status` |

### Domain-Specific Risk Factors
Depending on `policy_type`, the following fields are evaluated:
- **Auto Insurance:**
  - `telematics_score` (Float 0 - 100): Driving telemetry index (braking, cornering, speed).
  - `traffic_violations_last_3_years` (Integer): Moving violations on MVR.
  - `vehicle_annual_mileage` (Float): Annual commute distance.
- **Property Insurance:**
  - `property_age_years` (Integer): Dwelling construction age.
  - `roof_condition_score` (Float 0 - 10): Condition rating (10 = pristine new).
  - `flood_zone` (Boolean): Located in designated FEMA flood hazard zone.
  - `wildfire_risk_score` (String): `"Low"`, `"Moderate"`, `"High"`, `"Extreme"`.
  - `security_system_installed` (Boolean): 24/7 central station alarm protection.
- **Health & Life Insurance:**
  - `smoker_status` (Boolean): Tobacco/nicotine usage indicator.
  - `bmi` (Float): Body Mass Index (kg/m²).
  - `pre_existing_conditions` (Array of Strings): e.g. `["Hypertension", "Type II Diabetes"]`.
  - `family_medical_history_risk` (String): `"Standard"`, `"Elevated"`, `"Significant"`.

---

## 3. Data Preprocessing & Normalization Formulas

To transform fragmented raw inputs into actionable underwriting intelligence, the preprocessor executes the following transformations:

1. **Loss-to-Coverage Ratio (\(LCR\))**:
   $$\text{LCR} = \frac{\text{total\_incurred\_amount}}{\text{coverage\_amount}}$$
   *Flags severe loss exposure if \(LCR > 0.40\).*

2. **Claim Velocity Rate (\(CVR\))**:
   $$\text{CVR} = \frac{\text{claims\_last\_3\_years}}{3.0}$$
   *Identifies high-frequency loss trends if \(\ge 0.67\) claims/year.*

3. **At-Fault Liability Ratio (\(AFR\))**:
   $$\text{AFR} = \frac{\text{at\_fault\_claims\_count}}{\max(\text{total\_claims}, 1)}$$

4. **Normalized Credit Score**:
   Mapped dynamically to a 0–100 scale:
   - Excellent: $90$
   - Good: $75$
   - Fair: $50$
   - Poor: $25$

---

## 4. Privacy & Synthetic Data Guardrail
The preprocessor incorporates a real-time sanitization filter:
- Intercepts and strips keys containing: `name`, `full_name`, `ssn`, `phone`, `email`, `address`, `street`.
- Replaces regex-matched patterns (e.g., SSN pattern `\d{3}-\d{2}-\d{4}` and email addresses) with `[ANONYMIZED]`.
- Emits explicit audit warning flags to ensure absolute regulatory compliance.
