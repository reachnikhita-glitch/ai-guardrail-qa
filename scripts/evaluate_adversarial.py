
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
        for line_number, line in enumerate(dataset_file, start=1):
            if not line.strip():
                continue

            try:
                case = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on dataset line {line_number}"
                ) from exc

            results.extend(evaluate_case(case))

    if not results:
        raise ValueError("The adversarial dataset contains no test cases.")

    matches = sum(result["match"] for result in results)

    print("\nADVERSARIAL GUARDRAIL EVALUATION")
    print("-" * 72)

    for result in results:
        status = "MATCH" if result["match"] else "MISMATCH"
        print(
            f"{result['id']} | {result['guardrail']} | "
            f"expected={result['expected']} | "
            f"actual={result['actual']} | {status}"
        )

    print("-" * 72)
    print(f"Checks evaluated: {len(results)}")
    print(f"Matches: {matches}")
    print(f"Mismatches: {len(results) - matches}")
    print(f"Agreement: {matches / len(results):.1%}")

    print("\nPER-GUARDRAIL METRICS")
    print("-" * 72)

    for guardrail in sorted({r["guardrail"] for r in results}):
        group = [r for r in results if r["guardrail"] == guardrail]

        tp = sum(
            r["expected"] == "FAIL" and r["actual"] == "FAIL"
            for r in group
        )
        fp = sum(
            r["expected"] == "PASS" and r["actual"] == "FAIL"
            for r in group
        )
        fn = sum(
            r["expected"] == "FAIL" and r["actual"] == "PASS"
            for r in group
        )
        tn = sum(
            r["expected"] == "PASS" and r["actual"] == "PASS"
            for r in group
        )

        detection_rate = tp / (tp + fn) if tp + fn else None
        false_positive_rate = fp / (fp + tn) if fp + tn else None

        print(f"\n{guardrail}")
        print(f"  True positives:  {tp}")
        print(f"  False positives: {fp}")
        print(f"  False negatives: {fn}")
        print(f"  True negatives:  {tn}")
        print(
            "  Detection rate:  "
            + (f"{detection_rate:.1%}" if detection_rate is not None
               else "N/A (no attack cases)")
        )
        print(
            "  False positive rate: "
            + (f"{false_positive_rate:.1%}"
               if false_positive_rate is not None
               else "N/A (no safe cases)")
        )

    print(
        "\nInterpretation: these metrics describe only this dataset. "
        "Broader testing is needed before drawing conclusions about "
        "real-world safety."
    )


if __name__ == "__main__":
    main()
