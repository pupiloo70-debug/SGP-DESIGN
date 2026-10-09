"""Updated 2026-10-09; retained filename for GitHub replacement compatibility.
Original seven regression fixtures + seven type/unknown/burden/control fixtures.
"""
import json
import platform
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent

def assert_subset(test, actual, expected):
    for key, value in expected.items():
        test.assertIn(key, actual)
        if isinstance(value, dict):
            assert_subset(test, actual[key], value)
        else:
            test.assertEqual(actual[key], value, key)


def main():
    run = subprocess.run([sys.executable, str(HERE / 'run_vos_reproduction.py')], cwd=HERE, capture_output=True, text=True)
    print('COMMAND: python3 run_vos_reproduction.py\nEXIT: ' + str(run.returncode), flush=True)
    print(run.stdout, end='', flush=True)
    print(run.stderr, end='', flush=True)
    if run.returncode:
        raise SystemExit(run.returncode)
    actual = json.loads(run.stdout)
    cases = json.loads((HERE / 'vos_counterexamples.json').read_text())
    suite = unittest.TestSuite()
    for fixture, result in zip(cases, actual['counterexamples'], strict=True):
        def check(fixture=fixture, result=result):
            test = unittest.TestCase()
            test.assertEqual(result['name'], fixture['name'])
            assert_subset(test, result, fixture['expected'])
            test.assertIsNone(result['exception'])
        suite.addTest(unittest.FunctionTestCase(check, description=fixture['name']))
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
    report = {'schema':'SGP-QSV-CODEX-LOCAL-REPRODUCTION/0.2','date':'2026-10-09',
        'runtime':platform.python_version(),'command':'python3 R3-20261008-review.py',
        'supplied_runner_exit_code':run.returncode,'tests_run':result.testsRun,
        'original_regression_cases':7,'additional_cases':7,
        'failures':len(result.failures),'errors':len(result.errors),
        'tested_corrections_pass':result.wasSuccessful(),
        'closed_probes':['list_access','missing_risk_defaults','burden_increased'],
        'implementation_pass':False,'r3_approval':False,'deployment':False,
        'review_scope':'Only this corrected Grok-derived candidate; no V6/V7/V8 full regression or original evidence audit.',
        'canonical_axiom_mapping':'NOT_VERIFIED',
        'remaining_limits':['Uncalibrated illustrative support weights','No independent risk/evidence authentication','Question/revision/controller workflow not implemented','Only repeat-unit burden; no cost/time prediction audit']}
    (HERE / 'R3-20261008-codex-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
    raise SystemExit(0 if result.wasSuccessful() else 1)

if __name__ == '__main__':
    main()
