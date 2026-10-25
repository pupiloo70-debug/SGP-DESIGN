import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cri01 import evaluate

def example():
    return {'indicators': {k: {'status': 'VERIFIED', 'value': .5, 'sources': ['synthetic://test']} for k in 'EDCVR'}}

class CRITest(unittest.TestCase):
    def test_half(self):
        self.assertEqual(evaluate(example())['score'], 50.0)
    def test_unknown_not_zero(self):
        d = example()
        d['indicators']['E'] = {'status':'UNKNOWN'}
        self.assertIsNone(evaluate(d)['score'])
    def test_unavailable_not_zero(self):
        d = example()
        d['indicators']['D'] = {'status':'UNAVAILABLE'}
        self.assertIsNone(evaluate(d)['score'])
    def test_source_required(self):
        d=example()
        d['indicators']['E']['sources']=[]
        with self.assertRaises(ValueError):evaluate(d)
    def test_range(self):
        d=example()
        d['indicators']['E']['value']=2
        with self.assertRaises(ValueError):evaluate(d)
