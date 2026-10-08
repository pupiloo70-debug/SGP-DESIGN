"""Independent local checks of the supplied research candidate; not adoption."""
import json
import platform
import subprocess
import sys
from pathlib import Path
import vos_objective_candidate as vos

HERE = Path(__file__).resolve().parent

def main():
    run = subprocess.run([sys.executable, str(HERE/'run_vos_reproduction.py')], cwd=HERE, capture_output=True, text=True)
    actual = json.loads((HERE/'vos_reproduction_output.json').read_text())
    reported = json.loads((HERE/'grok_reported_reproduction_output.json').read_text())
    valid = run.returncode == 0 and actual == reported and len(actual['counterexamples']) == 7
    valid = valid and all(r.get('exception') is None and r.get('eligible_for_display') is False and r.get('illustrative_score') is None and r.get('immunity') is False for r in actual['counterexamples'])
    base = dict(issue_id='additional_probe', existing_record_reused=True, source_access='ORIGINAL', controller_named=True, unanswered_specified=True, new_procedure_recommended=False, existing_tasks_listed_first=True, victim_repeat_units_before=1, victim_repeat_units_after=1)
    probes=[]
    for name, changes in [('burden_increased',{'victim_repeat_units_after':100}),('list_access',{'source_access':[]}),('missing_risk_defaults',{})]:
        try:
            ev=vos.evaluate(vos.IssueInput(**(base|changes)))
            probes.append({'probe':name,'eligible_for_display':ev.eligible_for_display,'score':ev.illustrative_score,'burden_delta':ev.components.get('victim_burden_delta'),'exception':None})
        except Exception as exc:
            probes.append({'probe':name,'exception':type(exc).__name__,'message':str(exc)})
    result={'schema':'SGP-QSV-CODEX-LOCAL-REPRODUCTION/0.1','date':'2026-10-08','runtime':platform.python_version(),'command':'python3 R3-20261008-review.py','supplied_runner_exit_code':run.returncode,'seven_supplied_cases_match_reported_output':valid,'supplied_case_count':7,'additional_probes':probes,'remaining_defect_count':3,'review_scope':'Provided Grok candidate only; not Gemini/DeepSeek/V6/V7/V8 full regression','implementation_pass':False,'r3_approval':False,'deployment':False,'canonical_axiom_mapping':'NOT_VERIFIED'}
    (HERE/'R3-20261008-codex-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print('=== Supplied runner stdout ===\n'+run.stdout)
    print('=== Supplied runner stderr ===\n'+run.stderr)
    print('=== Independent review ===\n'+json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    if not valid: raise SystemExit(1)

if __name__=='__main__': main()
