import unittest
from copy import deepcopy
from ct045_execution_support import evaluate
class Tests(unittest.TestCase):
 def test_unknown_keeps_support(self):
  r=evaluate({});self.assertEqual(r['status'],'REVIEW_SUPPORT_PREPARED');self.assertTrue(r['allowed_support_actions'])
 def test_high_not_violation(self):
  r=evaluate({'unfounded_guilt_risk':'HIGH'});self.assertIn('HIGH_RISK_REVIEW_REQUIRED_NOT_CONFIRMED_VIOLATION',r['conclusion_holds']);self.assertFalse(r['facts_automatically_confirmed'])
 def test_authority_closure(self):self.assertIn('AUTHORITY_ONLY_CLOSURE_BLOCKED',evaluate({'closure_based_only_on_authority':True})['conclusion_holds'])
 def test_missing_metrics_not_gate(self):self.assertEqual(evaluate({})['status'],'REVIEW_SUPPORT_PREPARED')
 def test_sent_not_owner(self):self.assertEqual(evaluate({'owner_acceptance_receipt':{'state':'SENT'}})['owner_state'],'PROCESS_ASSIGNMENT_GAP')
 def test_scalar_owner_invalid(self):self.assertEqual(evaluate({'owner_acceptance_receipt':'SENT'})['status'],'INVALID_INPUT')
 def test_owner_requires_evidence(self):self.assertEqual(evaluate({'owner_acceptance_receipt':{'state':'OWNER_ACCEPTED'}})['owner_state'],'PROCESS_ASSIGNMENT_GAP')
 def test_controller_not_owner(self):self.assertEqual(evaluate({'record_controller':'NFS'})['owner_state'],'PROCESS_ASSIGNMENT_GAP')
 def test_partial_not_complete(self):self.assertEqual(evaluate({'completion_claimed':True,'completion_evidence':{'sources':['A'],'read_scope':'PARTIAL','executed':True}})['completion_state'],'UNVERIFIED_COMPLETION')
 def test_full_report_not_autoverified(self):self.assertEqual(evaluate({'completion_claimed':True,'completion_evidence':{'sources':['A'],'read_scope':'FULL','executed':True}})['completion_state'],'COMPLETION_REPORTED_REQUIRES_VERIFICATION')
 def test_no_input_mutation(self):
  x={'unanswered_items':[{'issue_id':'A','source_locations':['x']}]};old=deepcopy(x);r=evaluate(x);r['unique_issue_map']['A'].append('y');self.assertEqual(x,old)
 def test_same_issue_multiple_sources(self):self.assertEqual(evaluate({'unanswered_items':[{'issue_id':'A','source_locations':['y','x']},{'issue_id':'A','source_locations':['z']}]})['unique_issue_map'],{'A':['x','y','z']})
 def test_different_issues_preserved(self):self.assertEqual(len(evaluate({'unanswered_items':[{'issue_id':'A','source_locations':[]},{'issue_id':'B','source_locations':[]}]})['unique_issue_map']),2)
 def test_missing_clock_unverified(self):self.assertEqual(evaluate({})['clock']['status'],'CLOCK_UNVERIFIED')
 def test_date_only_unverified(self):self.assertEqual(evaluate({'internal_intake_timestamp':'2026-10-12'})['clock']['status'],'CLOCK_UNVERIFIED')
 def test_arbitrary_timestamp_unverified(self):self.assertEqual(evaluate({'internal_intake_timestamp':'xx'})['clock']['status'],'CLOCK_UNVERIFIED')
 def test_timestamp_requires_evidence(self):self.assertEqual(evaluate({'internal_intake_timestamp':'2026-10-12T17:00:00+09:00'})['clock']['status'],'CLOCK_UNVERIFIED')
 def test_calendar_not_assumed(self):
  r=evaluate({'internal_intake_timestamp':'2026-10-12T17:00:00+09:00','intake_evidence_ref':'A'})['clock'];self.assertEqual(r['preservation_target'],'2026-10-15T17:00:00+09:00');self.assertEqual(r['business_day_targets'],'PENDING_VALIDATED_ROUTE_CALENDAR');self.assertFalse(r['overdue_determined'])
 def test_missing_burden_not_zero(self):self.assertEqual(evaluate({})['burden_comparison']['labor_hours_delta'],'UNKNOWN')
 def test_no_unapproved_scores(self):self.assertIsNone(evaluate({})['support_score']);self.assertIsNone(evaluate({})['burden_penalty'])
 def test_input_level_does_not_transition(self):self.assertFalse(evaluate({'r26_level':'R2.6-4'})['case_transition'])
 def test_invalid_risk_type(self):self.assertEqual(evaluate({'unfounded_guilt_risk':[]})['status'],'INVALID_INPUT')
 def test_no_external_actions(self):self.assertEqual(evaluate({})['external_delivery'],'NOT_SENT');self.assertFalse(evaluate({})['runtime_deployed'])
if __name__=='__main__':unittest.main()
