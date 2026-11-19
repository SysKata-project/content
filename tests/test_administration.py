from copy import deepcopy
import json
import hashlib
from pathlib import Path
from subprocess import CompletedProcess
import unittest

import yaml

from scripts.compile_bundle import load_source, compile_bundle
from scripts.validate_administration import authorization_denied, quota_denied, manifest_matches, quota_matches

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / 'drafts/0.3.0'


class AdministrationTests(unittest.TestCase):
    def test_recorded_proof_matches_current_inputs(self):
        report = json.loads((DRAFT / 'checkpoint/evidence/2026-11-19-administration.json').read_text())
        self.assertTrue(report['validation_passed'])
        self.assertTrue(report['cleanup_passed'])
        self.assertEqual(102, len(report['checks']))
        self.assertTrue(all(check['passed'] for check in report['checks']))
        self.assertFalse(report['production_evaluator'])
        for name, digest in report['inputs_sha256'].items():
            with self.subTest(input=name):
                self.assertEqual(digest, hashlib.sha256((ROOT / name).read_bytes()).hexdigest())

    def test_complete_draft_compiles_without_answer_leakage(self):
        catalog = load_source(DRAFT / 'catalog.yaml')
        cases = json.loads((DRAFT / 'assessment-cases.json').read_text())
        files = compile_bundle(catalog, cases, 'a' * 40)
        self.assertFalse(json.loads(files['manifest.json'])['release_eligible'])
        learner = files['learner.json'].decode()
        for field in ['accepted_commands', 'correct_option_id', 'correct_order', 'reveal_markdown']:
            self.assertNotIn('"' + field + '"', learner)
        lessons = [e for e in catalog['entities'] if e['kind'] == 'lesson']
        self.assertEqual(7, len(lessons))
        for lesson in lessons:
            self.assertEqual(4, len(lesson['exercise_ids']))
        self.assertEqual(['oc-network'], next(e for e in lessons if e['id'] == 'oc-declarative')['prerequisites'])

    def test_infrastructure_failures_never_prove_denial(self):
        for stderr in ['connection refused', 'Unauthorized', 'i/o timeout', 'exceeded quota: exercise-budget']:
            result = CompletedProcess([], 1, '', stderr)
            self.assertFalse(authorization_denied(result))
            self.assertFalse(quota_denied(result))
        self.assertTrue(authorization_denied(CompletedProcess([], 1, '', 'Error (Forbidden)')))
        for stderr in ['Forbidden: exceeded quota: outer-budget', 'Forbidden: cannot create pods']:
            self.assertFalse(quota_denied(CompletedProcess([], 1, '', stderr)))
        self.assertTrue(quota_denied(CompletedProcess([], 1, '', 'Forbidden: exceeded quota: exercise-budget, pods=1')))

    def test_manifest_requires_latest_ready_state_and_security_fields(self):
        desired = yaml.safe_load((DRAFT / 'checkpoint/web.yaml').read_text())
        actual = deepcopy(desired)
        actual['metadata']['generation'] = 3
        actual['status'] = {'observedGeneration': 3, 'replicas': 1, 'updatedReplicas': 1, 'readyReplicas': 1}
        actual['spec']['template']['spec']['containers'][0]['securityContext']['runAsUser'] = 1001230000
        self.assertTrue(manifest_matches(actual, desired))
        stale = deepcopy(actual); stale['status']['observedGeneration'] = 2
        self.assertFalse(manifest_matches(stale, desired))
        unsafe = deepcopy(actual); unsafe['spec']['template']['spec']['automountServiceAccountToken'] = True
        self.assertFalse(manifest_matches(unsafe, desired))
        wrong = deepcopy(actual); wrong['spec']['template']['metadata']['labels']['exercise'] = 'wrong'
        self.assertFalse(manifest_matches(wrong, desired))
        old = deepcopy(actual); old['status']['updatedReplicas'] = 0
        self.assertFalse(manifest_matches(old, desired))

    def test_quota_requires_declared_and_accounted_limit(self):
        quota = {'spec': {'hard': {'pods': '1'}}, 'status': {'hard': {'pods': '1'}, 'used': {'pods': '1'}}}
        self.assertTrue(quota_matches(quota))
        for section, key, value in [('spec', 'hard', {'pods': '2'}), ('status', 'hard', {'pods': '2'}),
                                    ('status', 'used', {'pods': '0'})]:
            changed = deepcopy(quota); changed[section][key] = value
            self.assertFalse(quota_matches(changed))
        self.assertFalse(quota_matches({'spec': quota['spec']}))
