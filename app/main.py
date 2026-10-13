
from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.guardrails import (
    check_prompt_injection,
    check_sensitive_information,
)

app = FastAPI(
    title="AI Guardrail QA Framework",
    description="Automated testing for AI chatbot safety and compliance.",
    version="0.3.0",
)



from pydantic import BaseModel, Field, field_validator


class GuardrailRequest(BaseModel):
    response: str = Field(
        ...,
        min_length=1,
        description="Text to evaluate",
    )

    @field_validator("response")
    @classmethod
    def response_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Response must not be blank.")
        return value



@app.get("/")
def home():
    return {
        "message": "AI Guardrail QA Framework is running!",
        "status": "healthy",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/guardrails/sensitive-information")
def check_sensitive_info(request: GuardrailRequest):
    return check_sensitive_information(request.response)


@app.post("/guardrails/prompt-injection")
def check_prompt_injection_endpoint(request: GuardrailRequest):
    return check_prompt_injection(request.response)


@app.post("/guardrails/evaluate")
def evaluate_response(request: GuardrailRequest):
    """Run all configured guardrails and calculate overall risk."""

    checks = [
        check_sensitive_information(request.response),
        check_prompt_injection(request.response),
    ]

    failed_checks = [
        check for check in checks if check["status"] == "FAIL"
    ]

    severity_order = {
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3,
    }

    if not failed_checks:
        overall_status = "PASS"
        overall_risk = "LOW"
    else:
        overall_status = "FAIL"
        overall_risk = max(
            (check["severity"] for check in failed_checks),
            key=lambda severity: severity_order.get(severity, 0),
        )

    return {
        "overall_status": overall_status,
        "overall_risk": overall_risk,
        "total_checks": len(checks),
        "passed_checks": sum(
            check["status"] == "PASS" for check in checks
        ),
        "failed_checks": len(failed_checks),
        "results": checks,
    }
