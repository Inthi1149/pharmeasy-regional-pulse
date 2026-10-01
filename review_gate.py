import json
import uuid
from datetime import datetime, timezone


AUDIT_LOG_FILE = "audit_log.jsonl"

VALID_DECISIONS = {
    "approve",
    "edit",
    "reject",
}


def review_gate_v1(
    report,
    decision,
    reviewer_note="",
):
    """
    Human review gate for a generated report.

    Valid decisions:
        approve
        edit
        reject

    approve -> downstream use allowed
    edit    -> downstream use blocked
    reject  -> downstream use blocked
    """

    decision = decision.strip().lower()

    if decision not in VALID_DECISIONS:
        raise ValueError(
            "Invalid decision. "
            "Use approve, edit, or reject."
        )

    if not isinstance(report, dict):
        raise TypeError(
            "report must be a dictionary."
        )

    region = report.get(
        "region",
        "Unknown",
    )

    run_id = str(uuid.uuid4())

    downstream_allowed = (
        decision == "approve"
    )

    audit_entry = {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "run_id": run_id,
        "region": region,
        "decision": decision,
        "reviewer_note": reviewer_note,
    }

    with open(
        AUDIT_LOG_FILE,
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            json.dumps(audit_entry)
            + "\n"
        )

    updated_report = report.copy()
    updated_report["decision"] = decision
    updated_report["downstream_allowed"] = downstream_allowed

    return updated_report


def test_review_gate():
    sample_report = {
        "region": "Guntur",
        "context": (
            "Guntur sales were reviewed "
            "for April to June 2026."
        ),
        "insight": (
            "April-to-May sales increased "
            "by 122.19%."
        ),
        "implication": (
            "The movement requires "
            "human review before action."
        ),
    }

    print("\nTEST 1 - APPROVE")
    print("BEFORE:")
    print(sample_report)

    approve_result = review_gate_v1(
        sample_report,
        "approve",
        "Evidence checked; approved.",
    )

    print("AFTER:")
    print(approve_result)

    assert (
        approve_result["decision"]
        == "approve"
    )
    assert (
        approve_result["downstream_allowed"]
        is True
    )

    print("\nTEST 2 - EDIT")
    print("BEFORE:")
    print(sample_report)

    edit_result = review_gate_v1(
        sample_report,
        "edit",
        "Revise wording before use.",
    )

    print("AFTER:")
    print(edit_result)

    assert (
        edit_result["decision"]
        == "edit"
    )
    assert (
        edit_result["downstream_allowed"]
        is False
    )

    print("\nTEST 3 - REJECT")
    print("BEFORE:")
    print(sample_report)

    reject_result = review_gate_v1(
        sample_report,
        "reject",
        "Report rejected after review.",
    )

    print("AFTER:")
    print(reject_result)

    assert (
        reject_result["decision"]
        == "reject"
    )
    assert (
        reject_result["downstream_allowed"]
        is False
    )

    print("\nTEST 4 - INVALID INPUT")

    try:
        review_gate_v1(
            sample_report,
            "maybe",
            "Invalid decision test.",
        )

    except ValueError as error:
        print(
            "Invalid decision blocked:",
            error,
        )

    else:
        raise AssertionError(
            "Invalid decision was not blocked."
        )

    print("\nREVIEW GATE ACCEPTANCE CHECKS")
    print("-----------------------------")
    print("Approve path passed.")
    print("Edit path passed.")
    print("Reject path passed.")
    print("Invalid decision validation passed.")
    print(
        f"Audit entries appended to "
        f"{AUDIT_LOG_FILE}"
    )


if __name__ == "__main__":
    test_review_gate()