"""CT045-ES alignment reference 0.1.0. Tested source, not a deployed router.
No score, guilt, case-level transition, dispatch, or owner assignment is generated.
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from copy import deepcopy

VERSION = '0.1.0'
RULES = ['CT045-ES-%02d' % i for i in range(1,7)]
ACTIONS = ['PRESERVE_SOURCE_AND_PRIOR_STATE','PREPARE_PRODUCE_OR_EXPLAIN_PACKET','PREPARE_INDEPENDENT_REVIEW_ROUTE']
RISK_VALUES = {'LOW','MEDIUM','HIGH','UNKNOWN'}
TARGETS = {'preservation_hours':72,'assignment_business_days':5,'acquisition_and_plan_business_days':15,'initial_review_days':60,'extension_count_max':1,'extension_days_max':30}

def validate(data):
    errors=[]
    if not isinstance(data,dict): return ['input: expected object']
    for key in ('unfounded_guilt_risk','unfounded_immunity_risk'):
        if not isinstance(data.get(key,'UNKNOWN'),str) or data.get(key,'UNKNOWN') not in RISK_VALUES: errors.append(key+': invalid notation')
    for key in ('completion_claimed','closure_based_only_on_authority'):
        if key in data and not isinstance(data[key],bool): errors.append(key+': expected bool')
    items=data.get('unanswered_items',[])
    if not isinstance(items,list): errors.append('unanswered_items: expected list')
    else:
        for i,item in enumerate(items):
            if not isinstance(item,dict): errors.append(f'issue {i}: expected object');continue
            if not isinstance(item.get('issue_id'),str) or not item['issue_id'].strip(): errors.append(f'issue {i}: invalid issue_id')
            refs=item.get('source_locations',[])
            if not isinstance(refs,list) or any(not isinstance(x,str) or not x.strip() for x in refs): errors.append(f'issue {i}: invalid sources')
    for key in ('owner_acceptance_receipt','completion_evidence'):
        if data.get(key) is not None and not isinstance(data[key],dict): errors.append(key+': expected evidence object')
    return errors

def owner_state(data):
    r=data.get('owner_acceptance_receipt')
    fields=('owner','role','scope','source_ref','accepted_at')
    if not isinstance(r,dict) or r.get('state')!='OWNER_ACCEPTED' or r.get('capability_and_access_confirmed') is not True: return 'PROCESS_ASSIGNMENT_GAP'
    if any(not isinstance(r.get(k),str) or not r[k].strip() for k in fields): return 'PROCESS_ASSIGNMENT_GAP'
    return 'OWNER_ACCEPTANCE_REPORTED_REQUIRES_RECEIPT_VERIFICATION'

def clock_state(data):
    raw=data.get('internal_intake_timestamp')
    if not raw: return {'status':'CLOCK_UNVERIFIED','reason':'Missing timestamp does not prove clock never started','targets':deepcopy(TARGETS),'overdue_determined':False}
    try:
        t=datetime.fromisoformat(raw.replace('Z','+00:00'))
        if t.tzinfo is None: raise ValueError('timezone missing')
    except (AttributeError,TypeError,ValueError):
        return {'status':'CLOCK_UNVERIFIED','reason':'Invalid or date-only timestamp','targets':deepcopy(TARGETS),'overdue_determined':False}
    if not data.get('intake_evidence_ref'): return {'status':'CLOCK_UNVERIFIED','reason':'intake evidence missing','targets':deepcopy(TARGETS),'overdue_determined':False}
    k=t.astimezone(ZoneInfo('Asia/Seoul'))
    return {'status':'TARGET_CALCULATION_PREVIEW','origin':k.isoformat(),'preservation_target':(k+timedelta(hours=72)).isoformat(),'first_review_target':(k+timedelta(days=60)).isoformat(),'business_day_targets':'PENDING_VALIDATED_ROUTE_CALENDAR','targets':deepcopy(TARGETS),'overdue_determined':False,'statutory_deadline':False}

def burden_comparison(data):
    result={}
    for key in ('cost','labor_hours','waiting_days'):
        a=data.get('baseline',{});b=data.get('after_proposal',{})
        x=a.get(key) if isinstance(a,dict) else None;y=b.get(key) if isinstance(b,dict) else None
        from math import isfinite
        good=lambda v: isinstance(v,(int,float)) and not isinstance(v,bool) and isfinite(v) and v>=0
        result[key+'_delta']=y-x if good(x) and good(y) else 'UNKNOWN'
    result['burden_increase_reported']=any(isinstance(v,(int,float)) and v>0 for v in result.values())
    return result

def evaluate(data):
    errors=validate(data)
    if errors: return {'status':'INVALID_INPUT','errors':errors,'input_preserved':True,'case_transition':False,'runtime_deployed':False}
    issues={}
    for item in data.get('unanswered_items',[]):
        issues.setdefault(item['issue_id'],set()).update(item.get('source_locations',[]))
    risks=[data.get(k,'UNKNOWN') for k in ('unfounded_guilt_risk','unfounded_immunity_risk')]
    holds=[]
    if 'HIGH' in risks: holds.append('HIGH_RISK_REVIEW_REQUIRED_NOT_CONFIRMED_VIOLATION')
    if 'UNKNOWN' in risks: holds.append('RISK_ASSESSMENT_INCOMPLETE')
    if data.get('closure_based_only_on_authority'): holds.append('AUTHORITY_ONLY_CLOSURE_BLOCKED')
    completion='NOT_CLAIMED'
    if data.get('completion_claimed'):
        e=data.get('completion_evidence',{})
        if not isinstance(e,dict): e={}
        refs=e.get('sources',[])
        completion='COMPLETION_REPORTED_REQUIRES_VERIFICATION' if isinstance(refs,list) and refs and all(isinstance(x,str) and x.strip() for x in refs) and e.get('read_scope')=='FULL' and e.get('executed') is True else 'UNVERIFIED_COMPLETION'
        if completion=='UNVERIFIED_COMPLETION':holds.append(completion)
    return {'status':'REVIEW_SUPPORT_PREPARED','algorithm_version':VERSION,'rules':list(RULES),'allowed_support_actions':list(ACTIONS),'conclusion_holds':holds,'owner_state':owner_state(data),'completion_state':completion,'unique_issue_map':{k:sorted(v) for k,v in issues.items()},'burden_comparison':burden_comparison(data),'clock':clock_state(data),'support_score':None,'burden_penalty':None,'scoring_status':'UNAPPROVED_RESEARCH_FORMULA_NOT_USED','case_transition':False,'external_delivery':'NOT_SENT','runtime_deployed':False,'facts_automatically_confirmed':False}
