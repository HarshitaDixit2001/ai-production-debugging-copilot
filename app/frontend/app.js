"use strict";

const API = {
    analyze: "/incidents/analyze",
    health: "/health",
    ready: "/ready",
    evaluationSummary: "/evaluation/summary",
};

const elements = {
    form: document.getElementById("incident-form"),
    input: document.getElementById("incident-input"),
    count: document.getElementById("character-count"),
    analyzeButton: document.getElementById("analyze-button"),
    buttonLabel: document.getElementById("button-label"),
    buttonIcon: document.getElementById("button-icon"),

    apiDot: document.getElementById("api-dot"),
    apiState: document.getElementById("api-state"),
    modelDot: document.getElementById("model-dot"),
    modelState: document.getElementById("model-state"),
    refreshStatus: document.getElementById("refresh-status"),

    resultStatus: document.getElementById("result-status"),
    emptyState: document.getElementById("empty-state"),
    loadingState: document.getElementById("loading-state"),
    errorState: document.getElementById("error-state"),
    errorMessage: document.getElementById("error-message"),
    retryButton: document.getElementById("retry-button"),
    analysisResults: document.getElementById("analysis-results"),

    assessmentBadge: document.getElementById("assessment-badge"),
    diagnosis: document.getElementById("diagnosis-text"),
    incidentSummary: document.getElementById("incident-summary-text"),
    confidenceRing: document.getElementById("confidence-ring"),
    confidenceValue: document.getElementById("confidence-value"),
    confidenceCaption: document.getElementById("confidence-caption"),

    evidenceCount: document.getElementById("evidence-count"),
    evidenceList: document.getElementById("evidence-list"),
    causesList: document.getElementById("causes-list"),
    actionsList: document.getElementById("actions-list"),
    verificationList: document.getElementById("verification-list"),

    copyReport: document.getElementById("copy-report"),

        evaluationLoading: document.getElementById("evaluation-loading"),
    evaluationError: document.getElementById("evaluation-error"),
    evaluationErrorMessage: document.getElementById("evaluation-error-message"),
    evaluationMetrics: document.getElementById("evaluation-metrics"),
    refreshEvaluation: document.getElementById("refresh-evaluation"),

    evalAccuracy: document.getElementById("eval-accuracy"),
    evalCorrect: document.getElementById("eval-correct"),
    evalCoverage: document.getElementById("eval-coverage"),
    evalDiagnoses: document.getElementById("eval-diagnoses"),
    evalAbstention: document.getElementById("eval-abstention"),
    evalAbstentionCount: document.getElementById("eval-abstention-count"),
    evalCaseCount: document.getElementById("eval-case-count"),
    evalFailures: document.getElementById("eval-failures"),
};

let lastIncident = "";
let lastReport = null;

function setServiceStatus(dot, label, online, text) {
    dot.classList.toggle("online", online);
    dot.classList.toggle("offline", !online);
    label.textContent = text;
}

async function refreshServiceStatus() {
    elements.refreshStatus.disabled = true;
    elements.apiState.textContent = "Checking";
    elements.modelState.textContent = "Checking";

    try {
        const response = await fetch(API.health, {
            headers: { Accept: "application/json" },
            cache: "no-store",
        });

        if (!response.ok) {
            throw new Error(`Health check returned HTTP ${response.status}`);
        }

        const health = await response.json();
        const healthy = health.status === "healthy";

        setServiceStatus(
            elements.apiDot,
            elements.apiState,
            healthy,
            healthy ? "Online" : "Unavailable"
        );
    } catch {
        setServiceStatus(
            elements.apiDot,
            elements.apiState,
            false,
            "Offline"
        );
    }

    try {
        const response = await fetch(API.ready, {
            headers: { Accept: "application/json" },
            cache: "no-store",
        });

        const readiness = await response.json().catch(() => ({}));
        const ready = response.ok && readiness.status === "ready";

        setServiceStatus(
            elements.modelDot,
            elements.modelState,
            ready,
            ready ? "Ready" : "Unavailable"
        );
    } catch {
        setServiceStatus(
            elements.modelDot,
            elements.modelState,
            false,
            "Unavailable"
        );
    }

    elements.refreshStatus.disabled = false;
}


function formatPercentage(value) {
    const number = Number(value);

    if (!Number.isFinite(number) || number < 0 || number > 1) {
        return "N/A";
    }

    return `${Math.round(number * 100)}%`;
}

async function loadEvaluationSummary() {
    elements.refreshEvaluation.disabled = true;
    elements.evaluationLoading.hidden = false;
    elements.evaluationError.hidden = true;
    elements.evaluationMetrics.hidden = true;

    try {
        const response = await fetch(API.evaluationSummary, {
            headers: { Accept: "application/json" },
            cache: "no-store",
        });

        const data = await response.json().catch(() => null);

        if (!response.ok) {
            throw new Error(
                data?.detail || `Request failed with HTTP ${response.status}`
            );
        }

        if (
            !data ||
            typeof data !== "object" ||
            !Number.isFinite(data.total_cases) ||
            data.total_cases < 0 ||
            !Number.isFinite(data.correct) ||
            !Number.isFinite(data.diagnoses_provided)
        ) {
            throw new Error("The evaluation report has an invalid format.");
        }

        elements.evalAccuracy.textContent = formatPercentage(data.accuracy);
        elements.evalCorrect.textContent =
            `${data.correct} / ${data.total_cases} correct cases`;

        elements.evalCoverage.textContent = formatPercentage(data.coverage);
        elements.evalDiagnoses.textContent =
            `${data.diagnoses_provided} / ${data.total_cases} diagnoses provided`;

        const abstentionCases = Number(data.insufficient_evidence_cases);
        const abstentionCorrect = Number(data.insufficient_evidence_correct);

        if (
            Number.isFinite(abstentionCases) &&
            abstentionCases > 0 &&
            Number.isFinite(abstentionCorrect)
        ) {
            elements.evalAbstention.textContent = formatPercentage(
                data.insufficient_evidence_accuracy
            );

            elements.evalAbstentionCount.textContent =
                `${abstentionCorrect} / ${abstentionCases} cases handled correctly`;
        } else {
            elements.evalAbstention.textContent = "N/A";
            elements.evalAbstentionCount.textContent =
                "No insufficient-evidence cases evaluated";
        }

        elements.evalCaseCount.textContent = String(data.total_cases);

        const failed = Number.isFinite(data.failed_cases)
            ? data.failed_cases
            : 0;

        const errors = Number.isFinite(data.error_cases)
            ? data.error_cases
            : 0;

        elements.evalFailures.textContent =
            `${failed} failed · ${errors} errors`;

        elements.evaluationLoading.hidden = true;
        elements.evaluationMetrics.hidden = false;
    } catch (error) {
        elements.evaluationLoading.hidden = true;
        elements.evaluationMetrics.hidden = true;
        elements.evaluationError.hidden = false;

        elements.evaluationErrorMessage.textContent =
            error instanceof Error
                ? error.message
                : "Unable to load evaluation metrics.";
    } finally {
        elements.refreshEvaluation.disabled = false;
    }
}

function showState(state) {
    elements.emptyState.hidden = state !== "empty";
    elements.loadingState.hidden = state !== "loading";
    elements.errorState.hidden = state !== "error";
    elements.analysisResults.hidden = state !== "results";
}

function setBusy(busy) {
    elements.analyzeButton.disabled = busy;
    elements.input.disabled = busy;
    elements.buttonLabel.textContent = busy
        ? "Investigating incident..."
        : "Analyze incident";
    elements.buttonIcon.textContent = busy ? "◌" : "✳";
}

function setResultStatus(text, type = "") {
    elements.resultStatus.textContent = text;
    elements.resultStatus.className = "result-status";

    if (type) {
        elements.resultStatus.classList.add(type);
    }
}

function safeText(value, fallback = "Not provided") {
    if (value === null || value === undefined) {
        return fallback;
    }

    if (typeof value === "string") {
        return value.trim() || fallback;
    }

    if (typeof value === "number" || typeof value === "boolean") {
        return String(value);
    }

    try {
        return JSON.stringify(value, null, 2);
    } catch {
        return fallback;
    }
}

function makeEmptyMessage(message) {
    const node = document.createElement("div");
    node.className = "empty-list";
    node.textContent = message;
    return node;
}

function renderEvidence(evidence) {
    elements.evidenceList.replaceChildren();

    if (!Array.isArray(evidence) || evidence.length === 0) {
        elements.evidenceList.appendChild(
            makeEmptyMessage("No evidence was returned for this incident.")
        );
        elements.evidenceCount.textContent = "0";
        return;
    }

    elements.evidenceCount.textContent = String(evidence.length);

    evidence.forEach((item) => {
        const card = document.createElement("article");
        card.className = "evidence-item";

        const metadata = document.createElement("div");
        metadata.className = "evidence-meta";

        const source = document.createElement("span");
        source.className = "source-badge";
        source.textContent = safeText(item?.source, "Unknown source");
        metadata.appendChild(source);

        if (item?.chunk_id !== undefined && item?.chunk_id !== null) {
            const chunk = document.createElement("span");
            chunk.className = "source-badge";
            chunk.textContent = `Ref: ${safeText(item.chunk_id)}`;
            metadata.appendChild(chunk);
        }

        if (
            typeof item?.score === "number" &&
            Number.isFinite(item.score)
        ) {
            const score = document.createElement("span");
            score.className = "evidence-score";
            score.textContent = `Score ${item.score.toFixed(2)}`;
            metadata.appendChild(score);
        }

        const content = document.createElement("p");
        content.className = "evidence-content";
        content.textContent = safeText(item?.content);

        card.append(metadata, content);
        elements.evidenceList.appendChild(card);
    });
}

function renderList(container, items, options = {}) {
    container.replaceChildren();

    if (!Array.isArray(items) || items.length === 0) {
        container.appendChild(
            makeEmptyMessage(options.emptyMessage || "No items returned.")
        );
        return;
    }

    items.forEach((item, index) => {
        const row = document.createElement("div");
        row.className = "list-item";

        const marker = document.createElement("span");
        marker.className = "list-marker";

        if (options.checklist) {
            marker.textContent = "✓";
            marker.setAttribute("aria-hidden", "true");
        } else if (options.numbered) {
            marker.textContent = String(index + 1).padStart(2, "0");
        } else {
            marker.textContent = "•";
        }

        const text = document.createElement("span");
        text.textContent = safeText(item);

        row.append(marker, text);
        container.appendChild(row);
    });
}

function isInsufficientEvidence(diagnosis) {
    return safeText(diagnosis, "")
        .toLowerCase()
        .includes("insufficient evidence to determine the root cause");
}

function renderAnalysis(data) {
    elements.diagnosis.textContent = safeText(data.diagnosis);
    elements.incidentSummary.textContent = safeText(data.incident);
    elements.assessmentBadge.classList.remove("warning");

    const insufficient = isInsufficientEvidence(data.diagnosis);

    if (insufficient) {
        elements.assessmentBadge.textContent = "INSUFFICIENT EVIDENCE";
        elements.assessmentBadge.classList.add("warning");
        setResultStatus("INSUFFICIENT EVIDENCE", "warning");
    } else {
        elements.assessmentBadge.textContent = "ANALYSIS COMPLETE";
        setResultStatus("ANALYSIS COMPLETE", "complete");
    }

    const confidence = Number(data.confidence);
    const validConfidence =
        Number.isFinite(confidence) && confidence >= 0 && confidence <= 1;

    const percentage = validConfidence
        ? Math.round(confidence * 100)
        : 0;

    elements.confidenceValue.textContent = `${percentage}%`;
    elements.confidenceRing.style.background =
        `conic-gradient(var(--purple) ${percentage}%, #2b354b ${percentage}%)`;

    if (insufficient) {
        elements.confidenceCaption.textContent = "The available evidence was insufficient";
    } else if (!validConfidence) {
        elements.confidenceCaption.textContent = "Confidence value unavailable";
    } else if (percentage >= 75) {
        elements.confidenceCaption.textContent = "Higher model-reported confidence";
    } else if (percentage >= 40) {
        elements.confidenceCaption.textContent = "Moderate model-reported confidence";
    } else {
        elements.confidenceCaption.textContent = "Lower model-reported confidence";
    }

    renderEvidence(data.evidence);
    renderList(elements.causesList, data.possible_causes, {
        emptyMessage: "No additional causes were identified.",
    });
    renderList(elements.actionsList, data.recommended_actions, {
        numbered: true,
        emptyMessage: "No recommended actions were returned.",
    });
    renderList(elements.verificationList, data.verification_steps, {
        checklist: true,
        emptyMessage: "No verification steps were returned.",
    });

    lastReport = data;
    showState("results");
}

async function analyzeIncident(incident) {
    lastIncident = incident;
    setBusy(true);
    showState("loading");
    setResultStatus("INVESTIGATION IN PROGRESS");

    try {
        const response = await fetch(API.analyze, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Accept: "application/json",
            },
            body: JSON.stringify({ incident }),
        });

        const data = await response.json().catch(() => null);

        if (!response.ok) {
            let detail = data?.detail;

            if (Array.isArray(detail)) {
                detail = detail
                    .map((item) => item.msg || JSON.stringify(item))
                    .join("; ");
            }

            throw new Error(
                safeText(
                    detail,
                    `Request failed with HTTP ${response.status}`
                )
            );
        }

        if (
            !data ||
            typeof data !== "object" ||
            typeof data.diagnosis !== "string"
        ) {
            throw new Error("The API returned an unexpected response format.");
        }

        renderAnalysis(data);
        void refreshServiceStatus();
    } catch (error) {
        elements.errorMessage.textContent =
            error instanceof Error
                ? error.message
                : "An unexpected error occurred.";

        showState("error");
        setResultStatus("INVESTIGATION FAILED", "warning");
    } finally {
        setBusy(false);
    }
}

elements.input.addEventListener("input", () => {
    elements.count.textContent = `${elements.input.value.length} / 2000`;
});

document.querySelectorAll("[data-incident]").forEach((button) => {
    button.addEventListener("click", () => {
        elements.input.value = button.dataset.incident || "";
        elements.count.textContent = `${elements.input.value.length} / 2000`;
        elements.input.focus();
    });
});

elements.form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const incident = elements.input.value.trim();

    if (incident.length < 10 || incident.length > 2000) {
        elements.input.setCustomValidity(
            "Enter an incident description between 10 and 2000 characters."
        );
        elements.input.reportValidity();
        elements.input.setCustomValidity("");
        return;
    }

    await analyzeIncident(incident);
});

elements.retryButton.addEventListener("click", () => {
    if (lastIncident) {
        void analyzeIncident(lastIncident);
    }
});

elements.refreshStatus.addEventListener("click", () => {
    void refreshServiceStatus();
});

elements.copyReport.addEventListener("click", async () => {
    if (!lastReport) {
        return;
    }

    const report = [
        "AI PRODUCTION DEBUGGING COPILOT",
        "",
        `Incident: ${safeText(lastReport.incident)}`,
        `Diagnosis: ${safeText(lastReport.diagnosis)}`,
        `Confidence: ${Math.round(Number(lastReport.confidence) * 100)}%`,
        "",
        "EVIDENCE",
        ...(Array.isArray(lastReport.evidence)
            ? lastReport.evidence.map((item, index) =>
                `${index + 1}. ${safeText(item.source, "Unknown source")}: ${safeText(item.content)}`
            )
            : ["No evidence returned."]),
        "",
        "POSSIBLE CAUSES",
        ...(lastReport.possible_causes || []).map((item) => `- ${item}`),
        "",
        "RECOMMENDED ACTIONS",
        ...(lastReport.recommended_actions || []).map((item, index) =>
            `${index + 1}. ${item}`
        ),
        "",
        "VERIFICATION STEPS",
        ...(lastReport.verification_steps || []).map((item, index) =>
            `${index + 1}. ${item}`
        ),
        "",
        "Review evidence and verify findings before changing production systems.",
    ].join("\n");

    try {
        await navigator.clipboard.writeText(report);
        elements.copyReport.textContent = "Copied ✓";
        window.setTimeout(() => {
            elements.copyReport.textContent = "Copy report ↗";
        }, 1800);
    } catch {
        elements.copyReport.textContent = "Copy unavailable";
    }
});


if (elements.refreshEvaluation) {
    elements.refreshEvaluation.addEventListener("click", () => {
        void loadEvaluationSummary();
    });
}


showState("empty");
void refreshServiceStatus();
void loadEvaluationSummary();