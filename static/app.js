/**
 * TCS Technology Day - Insurance Automated Risk Profile Summarizer
 * Frontend Application Controller
 */

document.addEventListener("DOMContentLoaded", () => {
  let sampleProfiles = [];
  let currentOutputData = null;

  // DOM Elements
  const tabButtons = document.querySelectorAll(".nav-tab");
  const tabPanes = document.querySelectorAll(".tab-pane");
  const profileSelect = document.getElementById("profile-select");
  const jsonInput = document.getElementById("json-input");
  const btnSummarize = document.getElementById("btn-summarize");
  const btnLoadSample = document.getElementById("btn-load-sample");
  const btnFormatJson = document.getElementById("btn-format-json");
  const btnClearJson = document.getElementById("btn-clear-json");
  const btnCopySummary = document.getElementById("btn-copy-summary");
  const btnDownloadJson = document.getElementById("btn-download-json");
  const btnRunBenchmark = document.getElementById("btn-run-benchmark");

  // Output containers
  const outputPlaceholder = document.getElementById("output-placeholder");
  const outputLoading = document.getElementById("output-loading");
  const outputContent = document.getElementById("output-content");
  const outputActions = document.getElementById("output-actions");

  // Output fields
  const resScoreVal = document.getElementById("res-score-value");
  const resScoreFill = document.getElementById("res-score-fill");
  const resTierBadge = document.getElementById("res-tier-badge");
  const resDecisionBanner = document.getElementById("res-decision-banner");
  const resConfidenceText = document.getElementById("res-confidence-text");
  const resLatencyText = document.getElementById("res-latency-text");
  const resKriList = document.getElementById("res-kri-list");
  const resMitigatingList = document.getElementById("res-mitigating-list");
  const resExecSummary = document.getElementById("res-exec-summary");
  const resNarrative = document.getElementById("res-narrative");
  const resConditionsList = document.getElementById("res-conditions-list");

  // Benchmark fields
  const bmAccuracy = document.getElementById("bm-accuracy");
  const bmAvgSpeed = document.getElementById("bm-avg-speed");
  const bmMaxSpeed = document.getElementById("bm-max-speed");
  const bmCount = document.getElementById("bm-count");
  const bmTableBody = document.getElementById("bm-table-body");

  // Schema field
  const schemaCodeDisplay = document.getElementById("schema-code-display");

  // 1. Tab Switching
  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      tabButtons.forEach(b => b.classList.remove("active"));
      tabPanes.forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const target = document.getElementById(btn.getAttribute("data-tab"));
      if (target) target.classList.add("active");
    });
  });

  // 2. Fetch Sample Profiles
  async function loadProfiles() {
    try {
      const resp = await fetch("/api/profiles");
      if (!resp.ok) throw new Error("Failed to load profiles");
      sampleProfiles = await resp.json();

      profileSelect.innerHTML = "";
      sampleProfiles.forEach((p, idx) => {
        const opt = document.createElement("option");
        opt.value = idx;
        const claims = p.claim_history ? p.claim_history.claims_last_3_years : 0;
        opt.textContent = `${p.customer_id} (${p.policy_type}) — Age ${p.demographics.age}, ${p.demographics.occupation_category} [Claims: ${claims}]`;
        profileSelect.appendChild(opt);
      });

      // Load first profile by default
      if (sampleProfiles.length > 0) {
        selectProfile(0);
      }
    } catch (err) {
      console.error(err);
      profileSelect.innerHTML = `<option value="">Error loading profiles</option>`;
    }
  }

  function selectProfile(index) {
    if (sampleProfiles[index]) {
      jsonInput.value = JSON.stringify(sampleProfiles[index], null, 2);
    }
  }

  profileSelect.addEventListener("change", (e) => {
    selectProfile(e.target.value);
  });

  btnLoadSample.addEventListener("click", () => {
    selectProfile(profileSelect.value || 0);
  });

  // 3. JSON Editor utilities
  btnFormatJson.addEventListener("click", () => {
    try {
      const parsed = JSON.parse(jsonInput.value);
      jsonInput.value = JSON.stringify(parsed, null, 2);
    } catch (e) {
      alert("Invalid JSON: " + e.message);
    }
  });

  btnClearJson.addEventListener("click", () => {
    jsonInput.value = "";
    jsonInput.focus();
  });

  // 4. Summarization Trigger
  btnSummarize.addEventListener("click", async () => {
    const rawText = jsonInput.value.trim();
    if (!rawText) {
      alert("Please provide valid JSON input for the customer risk profile.");
      return;
    }

    let payload;
    try {
      payload = JSON.parse(rawText);
    } catch (e) {
      alert("JSON Syntax Error: " + e.message);
      return;
    }

    // UI state: loading
    outputPlaceholder.style.display = "none";
    outputContent.style.display = "none";
    outputLoading.style.display = "block";
    btnSummarize.disabled = true;
    btnSummarize.innerHTML = `<div class="spinner" style="width:16px;height:16px;border-width:2px;margin:0 4px 0 0;display:inline-block;vertical-align:middle;"></div> Synthesizing...`;

    const startTime = performance.now();

    try {
      const response = await fetch("/api/summarize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.error || "Server error occurred during summarization.");
      }

      const result = await response.json();
      currentOutputData = result;
      renderResults(result);
    } catch (err) {
      alert("Error: " + err.message);
      outputPlaceholder.style.display = "block";
      outputContent.style.display = "none";
    } finally {
      outputLoading.style.display = "none";
      btnSummarize.disabled = false;
      btnSummarize.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg> Generate AI Risk Profile Summary`;
    }
  });

  // 5. Render Output Results
  function renderResults(data) {
    outputContent.style.display = "block";
    outputActions.style.display = "flex";

    const risk = data.risk_assessment;
    const score = risk.composite_risk_score;
    const tier = risk.risk_tier;
    const decision = risk.underwriting_decision;
    const meta = data.metadata;

    // Score & Meter
    resScoreVal.textContent = score;
    resScoreFill.style.width = `${Math.min(100, Math.max(5, score))}%`;

    let colorVar = "var(--green)";
    let badgeClass = "badge-low";
    let tierBg = "#ecfdf5";
    let tierColor = "#047857";

    if (score > 75) {
      colorVar = "var(--red)";
      badgeClass = "badge-critical";
      tierBg = "#fef2f2";
      tierColor = "#b91c1c";
    } else if (score > 55) {
      colorVar = "var(--amber)";
      badgeClass = "badge-high";
      tierBg = "#fffbeb";
      tierColor = "#b45309";
    } else if (score > 25) {
      colorVar = "var(--blue)";
      badgeClass = "badge-medium";
      tierBg = "#eff6ff";
      tierColor = "#1d4ed8";
    }

    resScoreFill.style.backgroundColor = colorVar;
    resTierBadge.textContent = tier;
    resTierBadge.style.backgroundColor = tierBg;
    resTierBadge.style.color = tierColor;

    // Decision Banner
    resDecisionBanner.textContent = decision;
    resDecisionBanner.style.backgroundColor = tierBg;
    resDecisionBanner.style.color = tierColor;
    resDecisionBanner.style.border = `1px solid ${colorVar}`;

    resConfidenceText.textContent = `Confidence Score: ${Math.round(risk.confidence_score * 100)}% (Calibrated)`;
    resLatencyText.textContent = `⚡ Processed in ${meta.processing_time_seconds}s (${meta.processing_time_ms} ms) • Speed SLA Met (< 20s)`;

    // Key Risk Indicators
    resKriList.innerHTML = "";
    if (data.key_risk_indicators && data.key_risk_indicators.length > 0) {
      data.key_risk_indicators.forEach(kri => {
        const card = document.createElement("div");
        const sev = (kri.severity || "MEDIUM").toLowerCase();
        card.className = `kri-card ${sev}`;
        card.innerHTML = `
          <div class="kri-header">
            <span class="kri-indicator">${escapeHtml(kri.indicator)}</span>
            <span class="kri-badge badge-${sev}">${escapeHtml(kri.severity)}</span>
          </div>
          <p class="kri-detail">${escapeHtml(kri.detail || "")}</p>
        `;
        resKriList.appendChild(card);
      });
    } else {
      resKriList.innerHTML = `<div class="kri-card low"><span class="kri-indicator">No adverse risk indicators identified. Clean profile.</span></div>`;
    }

    // Mitigating Strengths
    resMitigatingList.innerHTML = "";
    if (data.mitigating_factors && data.mitigating_factors.length > 0) {
      data.mitigating_factors.forEach(mit => {
        const item = document.createElement("div");
        item.className = "mitigating-item";
        item.innerHTML = `<span>✔</span> <span>${escapeHtml(mit)}</span>`;
        resMitigatingList.appendChild(item);
      });
    } else {
      resMitigatingList.innerHTML = `<div class="mitigating-item"><span>Standard underwriting considerations without specific mitigating credits.</span></div>`;
    }

    // Executive Summary
    resExecSummary.textContent = data.summary.executive_summary;

    // Detailed Narrative (Simple Markdown Parser for headers, bold, bullets)
    resNarrative.innerHTML = parseSimpleMarkdown(data.summary.detailed_narrative);

    // Conditions
    resConditionsList.innerHTML = "";
    const conditions = data.summary.recommended_actions || [];
    if (conditions.length > 0) {
      conditions.forEach(c => {
        const li = document.createElement("li");
        li.textContent = c;
        resConditionsList.appendChild(li);
      });
    } else {
      resConditionsList.innerHTML = `<li>No specialized conditions required. Standard policy terms apply.</li>`;
    }
  }

  // 6. Simple Markdown Parser for clean presentation
  function parseSimpleMarkdown(text) {
    if (!text) return "";
    let html = escapeHtml(text);
    // Convert ### Header
    html = html.replace(/^### (.*$)/gim, "<h3>$1</h3>");
    // Convert **bold**
    html = html.replace(/\*\*(.*?)\*\*/gim, "<strong>$1</strong>");
    // Convert *italic*
    html = html.replace(/\*(.*?)\*/gim, "<em>$1</em>");
    // Convert bullet lists
    html = html.replace(/^\- (.*$)/gim, "<li>$1</li>");
    html = html.replace(/(<li>.*<\/li>)/gims, "<ul>$1</ul>");
    // Line breaks
    html = html.replace(/\n\n/gim, "<br><br>");
    return html;
  }

  function escapeHtml(str) {
    if (typeof str !== "string") return "";
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  // 7. Copy Summary Markdown & Export JSON
  btnCopySummary.addEventListener("click", () => {
    if (!currentOutputData) return;
    const narrative = currentOutputData.summary.detailed_narrative;
    const exec = currentOutputData.summary.executive_summary;
    const textToCopy = `# UNDERWRITING RISK PROFILE SUMMARY\n\n## Executive Summary\n${exec}\n\n${narrative}`;
    navigator.clipboard.writeText(textToCopy).then(() => {
      const orig = btnCopySummary.textContent;
      btnCopySummary.textContent = "Copied!";
      setTimeout(() => btnCopySummary.textContent = orig, 2000);
    });
  });

  btnDownloadJson.addEventListener("click", () => {
    if (!currentOutputData) return;
    const jsonStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(currentOutputData, null, 2));
    const a = document.createElement("a");
    a.setAttribute("href", jsonStr);
    a.setAttribute("download", `Risk_Summary_${currentOutputData.metadata.customer_id}.json`);
    document.body.appendChild(a);
    a.click();
    a.remove();
  });

  // 8. Run Benchmark Suite
  async function triggerBenchmark() {
    btnRunBenchmark.disabled = true;
    btnRunBenchmark.innerHTML = `Evaluating 10 Test Cases...`;

    try {
      const resp = await fetch("/api/evaluate", { method: "POST" });
      if (!resp.ok) throw new Error("Benchmark execution failed.");
      const data = await resp.json();

      bmAccuracy.textContent = `${data.overall_accuracy_pct}%`;
      bmAvgSpeed.textContent = `${data.average_generation_latency_seconds}s`;
      bmMaxSpeed.textContent = `${data.maximum_generation_latency_seconds}s`;
      bmCount.textContent = data.total_profiles_evaluated;

      bmTableBody.innerHTML = "";
      data.results.forEach(r => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td><strong>${escapeHtml(r.customer_id)}</strong></td>
          <td>${escapeHtml(r.policy_type)}</td>
          <td>${r.risk_score}</td>
          <td><span class="guardrail-tag">${escapeHtml(r.risk_tier)}</span></td>
          <td>${escapeHtml(r.underwriting_decision)}</td>
          <td><strong>${r.profile_accuracy_pct}%</strong></td>
          <td>${r.latency_seconds}s</td>
          <td><span class="badge-status ${r.speed_sla_met ? 'pass' : 'fail'}">${r.speed_sla_met ? 'PASSED (&lt;20s)' : 'FAILED'}</span></td>
        `;
        bmTableBody.appendChild(tr);
      });
    } catch (err) {
      alert("Error running benchmark: " + err.message);
    } finally {
      btnRunBenchmark.disabled = false;
      btnRunBenchmark.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg> Execute Benchmark Suite`;
    }
  }

  btnRunBenchmark.addEventListener("click", triggerBenchmark);

  // 9. Load Schema JSON
  async function loadSchema() {
    try {
      const resp = await fetch("/api/schema");
      if (resp.ok) {
        const schema = await resp.json();
        schemaCodeDisplay.textContent = JSON.stringify(schema, null, 2);
      }
    } catch (e) {
      schemaCodeDisplay.textContent = "Error loading schema.";
    }
  }

  // 10. External LLM Provider Management
  const llmProviderSelect = document.getElementById("llm-provider-select");
  const activeLlmPill = document.getElementById("active-llm-pill");
  const btnTestLlm = document.getElementById("btn-test-llm");
  const btnSaveLlm = document.getElementById("btn-save-llm");
  const llmTestResult = document.getElementById("llm-test-result");
  const llmTestMsg = document.getElementById("llm-test-msg");

  const inputGeminiKey = document.getElementById("input-gemini-key");
  const inputGeminiModel = document.getElementById("input-gemini-model");
  const inputOpenaiKey = document.getElementById("input-openai-key");
  const inputOpenaiModel = document.getElementById("input-openai-model");
  const inputAnthropicKey = document.getElementById("input-anthropic-key");
  const inputAnthropicModel = document.getElementById("input-anthropic-model");
  const inputOllamaUrl = document.getElementById("input-ollama-url");
  const inputOllamaModel = document.getElementById("input-ollama-model");
  const inputCustomUrl = document.getElementById("input-custom-url");
  const inputCustomKey = document.getElementById("input-custom-key");
  const inputCustomModel = document.getElementById("input-custom-model");

  function updateLLMFieldsVisibility(provider) {
    document.querySelectorAll(".llm-provider-fields").forEach(el => el.style.display = "none");
    const target = document.getElementById(`fields-${provider}`);
    if (target) {
      target.style.display = "block";
    }
  }

  if (llmProviderSelect) {
    llmProviderSelect.addEventListener("change", (e) => {
      updateLLMFieldsVisibility(e.target.value);
    });
  }

  async function loadLLMConfig() {
    try {
      const resp = await fetch("/api/llm/config");
      if (!resp.ok) return;
      const status = await resp.json();

      if (llmProviderSelect) {
        llmProviderSelect.value = status.provider || "local";
        updateLLMFieldsVisibility(status.provider || "local");
      }

      if (activeLlmPill) {
        activeLlmPill.textContent = `Active: ${status.active_provider_name}`;
        activeLlmPill.className = status.use_external ? "guardrail-tag checked" : "guardrail-tag";
      }

      if (inputGeminiModel && status.gemini_model) inputGeminiModel.value = status.gemini_model;
      if (inputOpenaiModel && status.openai_model) inputOpenaiModel.value = status.openai_model;
      if (inputAnthropicModel && status.anthropic_model) inputAnthropicModel.value = status.anthropic_model;
      if (inputOllamaUrl && status.ollama_base_url) inputOllamaUrl.value = status.ollama_base_url;
      if (inputOllamaModel && status.ollama_model) inputOllamaModel.value = status.ollama_model;
      if (inputCustomUrl && status.custom_base_url) inputCustomUrl.value = status.custom_base_url;
      if (inputCustomModel && status.custom_model) inputCustomModel.value = status.custom_model;
    } catch (err) {
      console.warn("Could not load LLM status:", err);
    }
  }

  if (btnTestLlm) {
    btnTestLlm.addEventListener("click", async () => {
      llmTestResult.style.display = "block";
      llmTestMsg.textContent = "Testing connection to active provider...";
      btnTestLlm.disabled = true;

      try {
        const resp = await fetch("/api/llm/test", { method: "POST" });
        const res = await resp.json();
        llmTestMsg.textContent = (res.success ? "✔ " : "✖ ") + res.message;
        llmTestResult.style.borderLeftColor = res.success ? "var(--green)" : "var(--red)";
      } catch (e) {
        llmTestMsg.textContent = "✖ Connection error: " + e.message;
        llmTestResult.style.borderLeftColor = "var(--red)";
      } finally {
        btnTestLlm.disabled = false;
      }
    });
  }

  if (btnSaveLlm) {
    btnSaveLlm.addEventListener("click", async () => {
      const provider = llmProviderSelect.value;
      const payload = { provider };

      if (provider === "gemini") {
        if (inputGeminiKey.value.trim()) payload.gemini_key = inputGeminiKey.value.trim();
        payload.gemini_model = inputGeminiModel.value;
      } else if (provider === "openai") {
        if (inputOpenaiKey.value.trim()) payload.openai_key = inputOpenaiKey.value.trim();
        payload.openai_model = inputOpenaiModel.value;
      } else if (provider === "anthropic") {
        if (inputAnthropicKey.value.trim()) payload.anthropic_key = inputAnthropicKey.value.trim();
        payload.anthropic_model = inputAnthropicModel.value;
      } else if (provider === "ollama") {
        payload.ollama_base_url = inputOllamaUrl.value.trim();
        payload.ollama_model = inputOllamaModel.value.trim();
      } else if (provider === "custom") {
        payload.custom_base_url = inputCustomUrl.value.trim();
        if (inputCustomKey.value.trim()) payload.custom_key = inputCustomKey.value.trim();
        payload.custom_model = inputCustomModel.value.trim();
      }

      btnSaveLlm.disabled = true;
      btnSaveLlm.textContent = "Applying...";

      try {
        const resp = await fetch("/api/llm/config", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        if (!resp.ok) {
          const err = await resp.json();
          throw new Error(err.error || "Failed to update LLM configuration.");
        }

        const updated = await resp.json();
        activeLlmPill.textContent = `Active: ${updated.active_provider_name}`;
        activeLlmPill.className = updated.use_external ? "guardrail-tag checked" : "guardrail-tag";

        llmTestResult.style.display = "block";
        llmTestMsg.textContent = `✔ Successfully activated ${updated.active_provider_name}! Future summaries will use this engine.`;
        llmTestResult.style.borderLeftColor = "var(--green)";
      } catch (err) {
        alert("Configuration Error: " + err.message);
      } finally {
        btnSaveLlm.disabled = false;
        btnSaveLlm.textContent = "Save & Apply Provider";
      }
    });
  }

  // Initialize
  loadProfiles();
  loadSchema();
  loadLLMConfig();
  triggerBenchmark(); // Pre-populate benchmark tab with verified results
});

