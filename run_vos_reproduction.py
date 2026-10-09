"""Run public fixtures and write full actual output. No adoption or approval."""
import json
from dataclasses import asdict
from pathlib import Path
import vos_objective_candidate as vos


def run_cases():
    here = Path(__file__).resolve().parent
    cases = json.loads((here / 'vos_counterexamples.json').read_text(encoding='utf-8'))
    results = []
    for source in cases:
        row = dict(source)
        name = row.pop('name')
        row.pop('expected', None)
        for key in vos.UNIT_FIELDS:
            if row.get(key) == 'NaN':
                row[key] = float('nan')
            elif row.get(key) == 'Infinity':
                row[key] = float('inf')
        try:
            actual = asdict(vos.evaluate(vos.IssueInput(issue_id=name, **row)))
            results.append({'name': name, 'exception': None, **actual})
        except Exception as exc:
            results.append({'name': name, 'exception': type(exc).__name__, 'error': str(exc)})
    return {'schema': 'SGP-QSV-LOCAL-REPRODUCTION/0.2', 'revision_date': '2026-10-09',
            'adoption': False, 'r3_approval': False, 'deployment': False,
            'counterexamples': results, 'lp728_gaps_outside_score': vos.LP728_GAPS_OUTSIDE_SCORE,
            'lp728_record_scope': 'Inherited submitter report; not independently reread by this code correction.'}


def main():
    payload = run_cases()
    text = json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
    (Path(__file__).resolve().parent / 'vos_reproduction_output.json').write_text(text, encoding='utf-8')
    print(text, end='')

if __name__ == '__main__':
    main()
