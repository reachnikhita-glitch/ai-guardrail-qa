# AI Guardrail QA Framework

## Overview

The AI Guardrail QA Framework is a Python-based prototype for testing AI chatbot responses against configurable safety checks. It provides automated checks for potentially sensitive information and common prompt-injection phrases, a REST API, and a small adversarial evaluation dataset.

The project demonstrates foundational skills in Python development, API implementation, automated testing, adversarial test design, and QA metric reporting.

## Objectives

- Detect potential email addresses and payment-card-like number patterns in chatbot responses.
- Flag configured prompt-injection phrases using normalized text matching.
- Expose guardrail checks through a REST API.
- Run repeatable automated tests and evaluate results against labeled test cases.
- Report evaluation metrics and document known limitations.

## Architecture

- `app/guardrails.py` — sensitive-information and prompt-injection detection logic.
- `app/main.py` — FastAPI application and unified guardrail evaluation endpoint.
- `tests/` — automated unit and API tests.
- `data/adversarial_cases.jsonl` — labeled adversarial and baseline test cases.
- `Scripts/evaluate_adversarial.py` — evaluation runner that compares actual detector outcomes with expected labels.

## Technology Stack

- Python
- FastAPI
- Pydantic
- pytest
- JSON Lines (JSONL)

## Getting Started

### Prerequisites

- Python installed
- Visual Studio Code or another code editor
- A terminal

### Install dependencies

Activate the project's virtual environment in PowerShell:


.\.venv\Scripts\Activate.ps1


Install the required packages if needed:


python -m pip install fastapi "uvicorn[standard]" pytest httpx


### Run the API

From the project root:


python -m uvicorn app.main:app --reload


Open the interactive API documentation at:

http://127.0.0.1:8000/docs

Check the health endpoint at:

http://127.0.0.1:8000/health

Press `Ctrl+C` in the terminal to stop the server.

## Available Guardrail Endpoints

- `GET /` — basic application information.
- `GET /health` — health check.
- `POST /guardrails/sensitive-information` — checks for configured sensitive-information patterns.
- `POST /guardrails/prompt-injection` — checks for configured prompt-injection phrases.
- `POST /guardrails/evaluate` — runs both checks and returns an overall result.

Example request body:


{
  "response": "Please contact customer@example.com for assistance."
}


The evaluation endpoint returns the results of the configured checks and an overall status and risk level.

## Run Automated Tests

From the project root:


python -m pytest -v


The current test suite contains 10 automated tests covering detector behavior, API responses, and empty-input validation.

## Run the Adversarial Evaluation

Run:


python -m Scripts.evaluate_adversarial


The evaluation runner processes the JSONL dataset, compares expected and actual results, and reports matches, mismatches, and per-guardrail metrics.

### Current Evaluation Results

The dataset contains 20 test cases, with two guardrail checks per case, for 40 total checks.

- Checks evaluated: 40
- Matches: 40
- Mismatches: 0
- Agreement with current dataset labels: 100%

These results measure agreement with the current expected labels. They do not establish production readiness or prove real-world detection accuracy.

## Known Limitations

- Prompt-injection detection relies on configured phrase matching and text normalization; it does not understand intent or meaning.
- Educational or quoted text containing a configured attack phrase may be flagged. This is a known false-positive risk.
- Unseen attack wording, obfuscation, and other adversarial inputs may evade the configured patterns.
- Sensitive-information checks use pattern matching and may miss valid formats or flag numbers that resemble payment-card data.
- The evaluation dataset is small and manually labeled. Its metrics are not representative of real-world traffic.
- This prototype does not replace security review, privacy controls, model-level safeguards, or production monitoring.

## Future Improvements

Potential next steps include expanding the labeled evaluation dataset, adding more unit and API tests, improving detector precision and recall, and introducing regression testing for newly discovered failure cases.

## Project Status

This is a portfolio-oriented QA prototype intended to demonstrate guardrail testing and evaluation fundamentals. It has not been validated for production use or independently assessed for regulatory or security compliance.