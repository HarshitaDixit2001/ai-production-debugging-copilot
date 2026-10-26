# AI Production Debugging Copilot

**An evidence-driven AI incident investigation system for diagnosing production failures, retrieving supporting evidence, and recommending corrective actions.**

Built with Python, FastAPI, retrieval-augmented generation (RAG), debugging tools, and a locally running LLM through Ollama.

## Overview

The AI Production Debugging Copilot helps engineers investigate production incidents by searching relevant logs, technical documentation, historical incidents, and code context. It aggregates the retrieved evidence and uses a local language model to generate a structured diagnosis.

The project focuses on **reliability, observability, evidence-based reasoning, and safe handling of insufficient evidence**.

Example incident:

`POST /payment is returning HTTP 500`

The system investigates the available context and returns a diagnosis, supporting evidence, confidence score, possible causes, recommended actions, and verification steps.

## Key Features

- **Incident analysis API** — submit production issues for investigation.
- **Retrieval-augmented generation (RAG)** — retrieve relevant context from project knowledge sources.
- **Tool-based investigation** — search application logs, documentation, incident history, and code.
- **Evidence aggregation** — combine relevant findings before generating a diagnosis.
- **Local LLM inference** — run analysis through Ollama without requiring a paid LLM API key.
- **Structured diagnosis** — provide possible causes, remediation actions, and verification steps.
- **Confidence scoring** — expose the model's reported confidence alongside its findings.
- **Insufficient-evidence handling** — return an explicit insufficient-evidence diagnosis when the available context does not support a root cause.
- **Reliability safeguards** — validate incident inputs, limit retrieval, and handle API errors.
- **Request tracing** — track requests using request IDs.
- **Reliability Console dashboard** — submit incidents, inspect results, and view evaluation metrics.
- **Evaluation pipeline** — compare generated diagnoses against expected outcomes.
- **Automated tests** — test API behavior, validation, retrieval, error handling, and evaluation functionality.

## Architecture

```text
                    Incident Report
                          |
                          v
                    FastAPI API
                          |
                          v
                    Incident Agent
                          |
             +------------+------------+
             |            |            |
             v            v            v
        Log Search   Documentation   Incident History
                         Search          Search
             |            |            |
             +------------+------------+
                          |
                          v
                   Code Context Search
                          |
                          v
                  Evidence Aggregation
                          |
                          v
                    Local LLM
                      (Ollama)
                          |
                          v
                  Structured Diagnosis
                          |
             +------------+-------------+
             |            |             |
             v            v             v
          Evidence    Confidence    Recommended
                                    Actions
                          |
                          v
                  Verification Steps
                          |
                          v
                 Reliability Console
```

### Main components

| Component | Responsibility |
|---|---|
| FastAPI | Exposes incident analysis and operational endpoints |
| Incident Agent | Coordinates investigation and analysis |
| Retrieval and tools | Search logs, documentation, incident history, and code context |
| Evidence aggregation | Collects relevant findings for the investigation |
| Ollama / local LLM | Generates a structured diagnosis using the supplied context |
| Evaluation pipeline | Measures diagnosis matching, coverage, and insufficient-evidence behavior |
| Frontend dashboard | Presents incident results and evaluation metrics |

## Technology Stack

- **Language:** Python
- **API framework:** FastAPI
- **LLM runtime:** Ollama
- **Retrieval:** Semantic search and RAG
- **Embeddings:** Sentence Transformers / `all-MiniLM-L6-v2`
- **Frontend:** HTML, CSS, JavaScript
- **Testing:** pytest
- **API validation:** Pydantic

## Getting Started

### Prerequisites

- Windows, macOS, or Linux
- Python version compatible with the project's dependencies
- Git
- Ollama
- Sufficient memory and disk space for the selected local models

### 1. Clone the repository

```bash
git clone https://github.com/HarshitaDixit2001/ai-production-debugging-copilot
cd ai-production-debugging-copilot
```

Replace the placeholder with your actual repository URL after publishing the project.

### 2. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

From the project root, install the dependencies declared by the repository:

```powershell
python -m pip install -r requirements.txt
```

### 4. Start Ollama and obtain the required models

Install Ollama from [ollama.com](https://ollama.com/) if it is not already installed.

The default configuration uses `qwen3:8b` for generation and `all-MiniLM-L6-v2` for embeddings. Confirm the model settings in `app/core/config.py` and any environment overrides before running the application.

Pull the configured generation model if necessary:

```powershell
ollama pull qwen3:8b
```

Ensure the Ollama service is running and that the configured embedding model can be loaded by the application.

### 5. Run the application

From the project root:

```powershell
uvicorn app.main:app --reload
```

Open the following URLs in your browser:

- Dashboard: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Interactive API documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- Readiness check: [http://127.0.0.1:8000/ready](http://127.0.0.1:8000/ready)
- Evaluation summary: [http://127.0.0.1:8000/evaluation/summary](http://127.0.0.1:8000/evaluation/summary)

The readiness endpoint checks whether the configured Ollama model is available. The evaluation summary endpoint reads the latest saved evaluation report.

## Using the Copilot

1. Open the Reliability Console dashboard.
2. Enter a production incident, such as `POST /payment is returning HTTP 500`.
3. Submit the incident for investigation.
4. Review the generated diagnosis, retrieved evidence, confidence, possible causes, recommended actions, and verification steps.
5. Review the evaluation metrics to understand the current measured performance.

**Important:** Treat generated diagnoses as investigation assistance, not as verified production facts. Validate the evidence and proposed actions before making changes to a live system.

## Evaluation

Run the evaluation pipeline from the project root:

```powershell
python scripts/run_evaluation.py
```

The generated report is saved to:

```text
evaluation/latest_report.json
```

The dashboard reads the saved report to display the current evaluation metrics.

### Latest evaluation results

The current evaluation run reported the following results on a dataset of four test cases.

| Metric | Result |
|---|---:|
| Test cases | 4 |
| Correct diagnoses | 4 |
| Diagnosis accuracy | 100% |
| Diagnosis coverage | 75% |
| Insufficient-evidence cases | 1 |
| Insufficient-evidence accuracy | 100% |
| Average reported confidence | 0.65 |
| Failed cases | 0 |
| Error cases | 0 |

These results reflect a small, four-case evaluation dataset and are not evidence of production-level accuracy. One timeout diagnosis did not match its expected diagnosis under the evaluator's current matching criteria. Diagnosis coverage was 75%, and the system correctly abstained on the single designated insufficient-evidence case. Model-reported confidence is not a calibrated probability of correctness.

### What is evaluated?

- Whether a generated diagnosis matches the expected diagnosis.
- Whether the system provides a diagnosis or appropriately abstains.
- Whether insufficient-evidence handling works on the designated test case.
- Whether confidence values are valid.
- Whether evaluation cases complete without execution errors.
- Whether model-provided evidence citations match retrieved source IDs, chunk IDs, or evidence     excerpts.
- Whether unsupported citations trigger safe abstention.


**Interpretation:** The 100% diagnosis accuracy is an observed result on only four test cases, not a reliable estimate of real-world performance. Diagnosis coverage of 75% means the system provided diagnoses for three cases and abstained on one. The reported confidence score is model output and is not a calibrated probability.

Evidence-citation validation checks whether model-provided citations correspond to retrieved evidence. It does not independently prove that every diagnosis is logically supported by its citations.

## Automated Tests

Run the complete test suite:

```powershell
pytest -q
```

The latest recorded full test run completed with **48 passed** and one non-blocking deprecation warning.

The suite covers core agent behavior, input validation, retrieval, tool limits, error handling, request IDs, health checks, and evaluation functionality.

Run the tests again after making changes to verify the current repository state.

## Project Structure

```text
ai-production-debugging-copilot/
├── app/
│   ├── agents/
│   ├── api/
│   ├── core/
│   ├── frontend/
│   │   ├── index.html
│   │   ├── styles.css
│   │   └── app.js
│   ├── models/
│   ├── services/
│   └── main.py
├── data/
│   ├── logs/
│   ├── docs/
│   ├── incidents/
│   └── code_context/
├── evaluation/
│   ├── dataset.json
│   └── latest_report.json
├── scripts/
│   └── run_evaluation.py
├── tests/
├── requirements.txt
└── README.md
```

This tree illustrates the main project areas; individual filenames may vary with the final repository structure.

## Limitations and Future Improvements

- The evaluation dataset currently contains only four cases and needs broader, more representative coverage.
- Diagnosis quality depends on the retrieved evidence, local model, and prompt.
- Model-reported confidence is not necessarily a calibrated probability of correctness.
- The system requires further evaluation against realistic incidents, ambiguous evidence, noisy logs, and failure scenarios before production use.
- Generated remediation steps require engineering review and should not be executed automatically without appropriate safeguards.
- Performance, latency, resource consumption, and retrieval quality should be measured under representative workloads.

Potential next improvements include expanding the evaluation dataset, adding regression tests for failure cases, improving evidence attribution, and tracking latency and retrieval quality.

## Engineering Focus

This project demonstrates practical work in:

- AI agent orchestration and tool-based investigation
- Retrieval-augmented generation over engineering knowledge
- Structured outputs and input validation
- Evaluation-driven development
- Safe abstention when evidence is insufficient
- API reliability and request tracing
- Local model integration
- Developer-facing observability and debugging interfaces

The goal is to demonstrate how an AI system can assist engineers with production troubleshooting while making its evidence, limitations, and recommended next steps visible.

---

**Project:** AI Production Debugging Copilot
**Focus:** Reliability engineering, AI-assisted incident investigation, RAG, evaluation, and observability
