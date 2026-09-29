# Demo Video Guide & Presentation Storyboard

## Overview
This document provides a step-by-step guide and script for recording the **Demo Video** showcasing summary generation as requested in the **TCS Technology Day** problem statement deliverables:
> *"Deliverables include simple UI or API interface, documentation on data schema and AI logic, and demo video showcasing summary generation."*

---

## Video Specifications
- **Recommended Length:** 2 to 3 minutes
- **Recommended Recording Tool:** OBS Studio, QuickTime Player (Screen Recording on Mac), Loom, or Microsoft Teams / Zoom recording
- **Resolution:** 1080p (1920x1080) or 720p
- **Audio:** Clear voiceover explaining key capabilities and metrics

---

## Step-by-Step Recording Script & Storyboard

### Scene 1: Introduction & Problem Context (0:00 - 0:30)
- **Visual:** Display the Web UI dashboard home screen at `http://localhost:8080`. Point to the header with **"TCS Technology Day - Insurance Automated Risk Profile Summarizer"**.
- **Voiceover Script:**
  > *"Hello everyone! Welcome to our demonstration of the Automated Risk Profile Summarizer for TCS Technology Day. 
  > In the insurance underwriting domain, underwriters spend hours manually compiling and interpreting risk data from fragmented sources—leading to slow cycle times and inconsistencies. 
  > Our solution is a high-performance Single-Agent GenAI system that automates the entire process: ingesting synthetic customer risk profiles, calculating Key Risk Indicators (KRIs), and generating synthesized, actionable underwriting summaries in under a fraction of a second—achieving 100% accuracy on our evaluation benchmarks, well above the 85% requirement."*

---

### Scene 2: Selecting a Profile & Generating Summary (0:30 - 1:15)
- **Visual:**
  1. Click the **"Preloaded Synthetic Profiles"** dropdown on the left.
  2. Select `CUST-AUTO-101 (Auto) — Age 42, Professional [Claims: 0]`.
  3. Briefly show the clean JSON structure (Demographics, Policy, Claims, Telematics).
  4. Click the large blue button: **"⚡ Generate AI Risk Profile Summary"**.
  5. Watch the dashboard populate immediately.
- **Voiceover Script:**
  > *"Let's test our first profile: a prime low-risk auto applicant, Customer AUTO-101. 
  > Notice the built-in guardrails on the left: automatic PII redaction to guarantee zero personal data exposure, and loss-ratio normalization.
  > When I click 'Generate AI Risk Profile Summary', our single agent runs preprocessing, scoring, and natural language synthesis instantaneously in under 0.05 seconds—easily meeting the sub-20-second SLA.
  > As you can see, the applicant receives a Composite Risk Score of 5/100, placed in the 'Low / Preferred' tier, with an 'Approve - Preferred Rates' decision. The system highlights mitigating strengths such as clean claims history and a 94/100 telematics defensive driving score."*

---

### Scene 3: Handling High-Risk & Complex Multi-Peril Case (1:15 - 1:55)
- **Visual:**
  1. In the dropdown, switch to a high-risk case: `CUST-PROP-201 (Property) — Age 51, Commercial Driving [Claims: 2]`.
  2. Point out the property has a 44-year-old roof, is located in a FEMA Flood Zone, and has an Extreme Wildfire hazard rating with $88,000 in prior claims.
  3. Click **"⚡ Generate AI Risk Profile Summary"**.
  4. Point to the red **Risk Score: 98/100 (High / Critical Risk)** and the decision banner: **"Decline Coverage"**.
  5. Scroll down to show the **Key Risk Indicators (KRIs)** chips (CRITICAL Flood Exposure, CRITICAL Wildfire Hazard, HIGH Structural Wear) and the markdown narrative with required endorsements.
- **Voiceover Script:**
  > *"Now, let's examine a complex high-risk property applicant: Customer PROP-201. 
  > This dwelling is located in a designated FEMA flood plain with extreme wildfire hazard and two prior water/roof claims.
  > The agent immediately identifies three Critical Key Risk Indicators, flags a 98/100 Risk Index, and recommends declining coverage or mandating senior underwriter review with flood exclusion riders.
  > Underwriters receive an executive summary, a 4-part actuarial narrative breakdown, and actionable endorsements—all generated automatically."*

---

### Scene 4: Live Accuracy & Speed Benchmark Verification (1:55 - 2:35)
- **Visual:**
  1. Click the second tab in the top navigation: **"Live Accuracy & Speed Benchmark"**.
  2. Point to the four headline metric cards:
     - **Accuracy Rate: 100.0%** (Passing \(\ge 85\%\))
     - **Average Generation Speed: < 0.001s** (Passing \(< 20\)s)
     - **Maximum Generation Latency: < 0.001s**
     - **Profiles Evaluated: 10**
  3. Click **"Execute Benchmark Suite"** to demonstrate live evaluation execution.
  4. Scroll through the results table showing 10 diverse profiles across Auto, Property, Health, and Life lines of business.
- **Voiceover Script:**
  > *"To rigorously validate our solution against the TCS Technology Day success criteria, we navigate to the Benchmark tab.
  > The problem statement mandated at least 85% accuracy and under 20 seconds generation speed.
  > As shown in our automated test suite evaluating 10 gold-standard ground-truth profiles across Auto, Property, Health, and Life lines of business, our system achieves a 100% accuracy score and generates summaries in less than a millisecond per case."*

---

### Scene 5: Data Schema, AI Logic & Conclusion (2:35 - 3:00)
- **Visual:**
  1. Quickly toggle to the **"Data Schema & Dictionary"** tab and the **"AI Logic & Architecture"** tab showing the flow diagram and decision matrix.
  2. Switch back to the underwriter workspace.
  3. Click **"Export JSON"** or **"Copy Markdown"** to show export capabilities.
- **Voiceover Script:**
  > *"The architecture is fully documented with a standardized JSON schema, PII sanitization guardrails, and deterministic plus LLM-compatible generative synthesis.
  > Underwriters can copy the synthesized markdown dossier or export the full JSON response with one click.
  > Thank you for watching our demonstration of the Automated Risk Profile Summarizer!"*

---

## Command to Run for the Demo
To start the application for your recording:
```bash
# In the project directory:
python3 app.py
```
Then open your browser to:
`http://localhost:8080`
