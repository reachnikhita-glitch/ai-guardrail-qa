
import json
from pathlib import Path

from app.guardrails import (
    check_prompt_injection,
    check_sensitive_information,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_PATH = PROJECT_ROOT / "data" / "adversarial_cases.jsonl"


def evaluate_case(case: dict) -> list[dict]:
    sensitive_result = check_sensitive_information(case["response"])
    injection_result = check_prompt_injection(case["response"])

    checks = [
        (
            "sensitive_information",
            case["expected_sensitive"],
            sensitive_result["status"],
        ),
        (
            "prompt_injection",
            case["expected_injection"],
            injection_result["status"],
        ),
    ]

    return [
        {
            "id": case["id"],
            "category": case["category"],
            "guardrail": guardrail,
            "expected": expected,
            "actual": actual,
            "match": expected == actual,
        }
        for guardrail, expected, actual in checks
    ]


def main():
    results = []

    with DATASET_PATH.open("r", encoding="utf-8") as dataset_file:
        for line in dataset_file:
            if line.strip():
                case = json.loads(line)
                results.extend(evaluate_case(case))

    total = len(results)
    matches = sum(result["match"] for result in results)
    mismatches = total - matches

    print("\nADVERSARIAL GUARDRAIL EVALUATION")
    print("-" * 72)

    for result in results:
        status = "MATCH" if result["match"] else "MISMATCH"
        print(
            f"{result['id']} | "
            f"{result['guardrail']} | "
            f"expected={result['expected']} | "
            f"actual={result['actual']} | "
            f"{status}"
        )

    print("-" * 72)
    print(f"Checks evaluated: {total}")
    print(f"Matches: {matches}")
    print(f"Mismatches: {mismatches}")

    if total:
        print(f"Agreement: {matches / total:.1%}")

    if mismatches:
        print(
            "\nReview mismatches as potential false positives or "
            "false negatives. Do not treat agreement alone as proof "
            "of safety."
        )


if __name__ == "__main__":
    main()
