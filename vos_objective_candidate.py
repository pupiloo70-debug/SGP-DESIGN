"""Defect-fixed research candidate. Not adopted. Not an R3 approval.

Revision: 2026-10-09. Local correction candidate, not a governance approval.

Confirmed defects closed here:
- non-bool values no longer score as true
- NaN and Inf no longer produce a score
- negative units and unknown access return a structured rejection,
  not ValueError and not immunity
LP728 record gaps stay outside the score.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


SOURCE_ACCESS = {"NOT_READ": 0.0, "SECONDARY": 0.5, "ORIGINAL": 1.0}
BOOL_FIELDS = (
    "existing_record_reused",
    "controller_named",
    "unanswered_specified",
    "new_procedure_recommended",
    "existing_tasks_listed_first",
    "closure_treated_as_verification",
    "gap_treated_as_immunity",
    "gap_treated_as_victim_fault",
    "crime_or_causation_asserted",
    "crime_elements_established",
    "unread_marked_complete",
    "emotion_used_as_credibility_penalty",
)
RISK_FIELDS = BOOL_FIELDS[5:]
UNIT_FIELDS = ("victim_repeat_units_before", "victim_repeat_units_after")


@dataclass
class IssueInput:
    issue_id: str
    existing_record_reused: Any
    source_access: Any
    controller_named: Any
    unanswered_specified: Any
    new_procedure_recommended: Any
    existing_tasks_listed_first: Any
    victim_repeat_units_before: Any
    victim_repeat_units_after: Any
    closure_treated_as_verification: Any = None
    gap_treated_as_immunity: Any = None
    gap_treated_as_victim_fault: Any = None
    crime_or_causation_asserted: Any = None
    crime_elements_established: Any = None
    unread_marked_complete: Any = None
    emotion_used_as_credibility_penalty: Any = None


@dataclass
class Evaluation:
    eligible_for_display: bool
    hard_violations: list[str]
    structure_errors: list[str]
    components: dict[str, Any]
    illustrative_score: float | None
    score_status: str
    immunity: bool = False
    cannot_decide: list[str] = field(default_factory=lambda: [
        "guilt", "causation", "compensation", "forfeiture", "rights_restriction", "adoption"
    ])


def _finite_nonnegative_int(value: Any) -> bool:
    if isinstance(value, bool) or not isinstance(value, int):
        return False
    return value >= 0


def structure_errors(item: IssueInput) -> list[str]:
    found = []
    for name in BOOL_FIELDS:
        if getattr(item, name) is None and name in RISK_FIELDS:
            continue
        if type(getattr(item, name)) is not bool:
            found.append(f"BOOL_TYPE:{name}")
    if not isinstance(item.source_access, str) or item.source_access not in SOURCE_ACCESS:
        found.append("SOURCE_ACCESS_NOT_VERIFIED")
    for name in UNIT_FIELDS:
        value = getattr(item, name)
        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            found.append(f"NONFINITE_UNITS:{name}")
        elif not _finite_nonnegative_int(value):
            found.append(f"UNIT_TYPE:{name}")
    return found


def hard_violations(item: IssueInput) -> list[str]:
    found = []
    if item.closure_treated_as_verification is True:
        found.append("CLOSURE_IS_NOT_VERIFICATION")
    if item.gap_treated_as_immunity is True:
        found.append("GAP_IS_NOT_IMMUNITY")
    if item.gap_treated_as_victim_fault is True:
        found.append("GAP_IS_NOT_VICTIM_FAULT")
    if item.crime_or_causation_asserted is True and item.crime_elements_established is not True:
        found.append("UNESTABLISHED_CRIME_OR_CAUSATION")
    if item.unread_marked_complete is True:
        found.append("UNREAD_MARKED_COMPLETE")
    if item.emotion_used_as_credibility_penalty is True:
        found.append("EMOTION_USED_AS_CREDIBILITY_PENALTY")
    if item.new_procedure_recommended is True and item.existing_tasks_listed_first is not True:
        found.append("NEW_PROCEDURE_BEFORE_EXISTING_TASKS")
    return found


def evaluate(item: IssueInput) -> Evaluation:
    errors = structure_errors(item)
    if errors:
        return Evaluation(
            False, [], errors, {}, None, "STRUCTURE_REJECTED_NOT_IMMUNITY", False
        )
    violations = hard_violations(item)
    access = SOURCE_ACCESS[item.source_access]
    reuse = 1.0 if item.existing_record_reused else 0.0
    identified = 1.0 if item.controller_named and item.unanswered_specified else 0.0
    burden_delta = item.victim_repeat_units_after - item.victim_repeat_units_before
    components = {
        "weight_status": "ILLUSTRATIVE_UNCALIBRATED",
        "source_access": access,
        "existing_reuse": reuse,
        "controller_and_gap_identified": identified,
        "victim_repeat_units_before": item.victim_repeat_units_before,
        "victim_repeat_units_after": item.victim_repeat_units_after,
        "victim_burden_delta": burden_delta,
        "burden_delta_definition": "AFTER_MINUS_BEFORE",
        "burden_warning": "BURDEN_INCREASED" if burden_delta > 0 else None,
        "risk_assessment_status": "UNKNOWN" if any(getattr(item, n) is None for n in RISK_FIELDS) else "EXPLICIT_VALUES_PROVIDED_NOT_INDEPENDENTLY_VERIFIED",
        "lp728_gaps_outside_score": True,
    }
    if violations:
        return Evaluation(False, violations, [], components, None, "BLOCKED_BY_HARD_CONSTRAINT", False)
    unknown = [name for name in RISK_FIELDS if getattr(item, name) is None]
    if unknown:
        components["unknown_risk_fields"] = unknown
        return Evaluation(False, [], [], components, None, "PENDING_RISK_ASSESSMENT", False)
    if burden_delta > 0:
        return Evaluation(False, [], [], components, None, "HELD_BURDEN_INCREASE", False)
    # Support-only illustrative score; burden cannot improve or offset it.
    score = (0.35 * access) + (0.25 * reuse) + (0.25 * identified)
    return Evaluation(
        True, [], [], components, round(min(score, 1.0), 4),
        "ILLUSTRATIVE_UNCALIBRATED_NOT_A_VERDICT", False
    )


LP728_GAPS_OUTSIDE_SCORE = {
    "case_id": "LP728-LOT00518001",
    "not_a_score": True,
    "agency_claim": {
        "16987007_items_1_2": "정보 부존재",
        "portal_status": "공개완료",
        "items_3_5": "research report referral only",
        "item_6_distinction_on_captures": "NOT_VISIBLE",
    },
    "substantive_evaluation": {
        "evaluator": "Grok 4.7",
        "report_body": "NOT_READ",
        "return_8_to_disposal_link": "UNRESOLVED",
        "disposal_reported_sum": 42,
        "conditional_pack_conversion": 51,
        "access_failure_is_not_family_proof_failure": True,
    },
}
