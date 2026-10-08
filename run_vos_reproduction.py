"""One-command reproduction. Prints counterexample results and LP728 gaps."""

import json
import math
from pathlib import Path

import vos_objective_candidate as vos


def load_value(value):
    if value == "NaN":
        return float("nan")
    if value == "Infinity":
        return float("inf")
    return value


def main() -> None:
    here = Path(__file__).resolve().parent
    rows = json.loads((here / "vos_counterexamples.json").read_text(encoding="utf-8"))
    results = []
    for row in rows:
        name = row.pop("name")
        item = vos.IssueInput(issue_id=name, **{key: load_value(value) for key, value in row.items()})
        try:
            ev = vos.evaluate(item)
            results.append({
                "name": name,
                "exception": None,
                "eligible_for_display": ev.eligible_for_display,
                "immunity": ev.immunity,
                "structure_errors": ev.structure_errors,
                "hard_violations": ev.hard_violations,
                "illustrative_score": ev.illustrative_score,
                "score_status": ev.score_status,
            })
        except Exception as exc:
            results.append({"name": name, "exception": type(exc).__name__, "error": str(exc)})
    payload = {
        "adoption": False,
        "r3_approval": False,
        "counterexamples": results,
        "lp728_gaps_outside_score": vos.LP728_GAPS_OUTSIDE_SCORE,
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False)
    (here / "vos_reproduction_output.json").write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
