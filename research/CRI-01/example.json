#!/usr/bin/env python3
"""Experimental verification-obstruction risk signals, not corruption findings."""
import json
import sys
from pathlib import Path

WEIGHTS = {'E': .30, 'D': .20, 'C': .20, 'V': .20, 'R': .10}
STATES = {'VERIFIED', 'DISPUTED', 'UNKNOWN', 'UNAVAILABLE', 'NOT_APPLICABLE'}

def evaluate(doc):
    indicators = doc.get('indicators')
    if not isinstance(indicators, dict) or set(indicators) != set(WEIGHTS):
        raise ValueError('indicators must contain exactly E,D,C,V,R')
    values, review, sources = {}, [], {}
    for key in WEIGHTS:
        item = indicators[key]
        if not isinstance(item, dict) or item.get('status') not in STATES:
            raise ValueError(f'{key}: invalid indicator/status')
        state = item['status']
        refs = item.get('sources', [])
        if not isinstance(refs, list) or not all(isinstance(x, str) and x.strip() for x in refs):
            raise ValueError(f'{key}: invalid sources')
        if state == 'VERIFIED':
            val = item.get('value')
            if isinstance(val, bool) or not isinstance(val, (int, float)) or not 0 <= val <= 1:
                raise ValueError(f'{key}: value must be 0..1')
            if not refs:
                raise ValueError(f'{key}: verified requires a source')
            values[key] = float(val)
        else:
            if item.get('value') is not None:
                raise ValueError(f'{key}: unresolved/nonapplicable status requires null or absent value')
            review.append({'indicator': key, 'status': state})
        sources[key] = refs
    complete = not review
    return {'schema': 'SGP-QSV-CRI-01-RESULT/0.1',
            'model_status': 'EXPERIMENTAL_RESEARCH',
            'evaluation_status': 'FULLY_SOURCED_PROTOTYPE_SCORE' if complete else 'INCOMPLETE_REQUIRES_REVIEW',
            'score': round(100 * sum(WEIGHTS[k] * values[k] for k in WEIGHTS), 4) if complete else None,
            'needs_review': review, 'sources': sources,
            'not_a_corruption_or_guilt_finding': True,
            'automatic_sanctions': False,
            'approval_of_civic_trace_046': False}

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python3 cri01.py input.json')
    print(json.dumps(evaluate(json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))), ensure_ascii=False, indent=2))
