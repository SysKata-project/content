from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from scripts.validate_foundations import current_rollout, repair_observed, load_feasibility, FAULT_IMAGE


class FoundationsEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.image = 'approved-image'
        self.initial = {
            'metadata': {'uid': 'original', 'generation': 1},
            'spec': {'replicas': 1, 'template': {'spec': {'containers': [{'image': self.image}]}}},
            'status': {'observedGeneration': 1, 'updatedReplicas': 1, 'readyReplicas': 1,
                       'replicas': 1, 'unavailableReplicas': 0},
        }
        self.fault = deepcopy(self.initial)
        self.fault['metadata']['generation'] = 2
        self.fault['spec']['template']['spec']['containers'][0]['image'] = FAULT_IMAGE
        self.repaired = deepcopy(self.initial)
        self.repaired['metadata']['generation'] = 3
        self.repaired['status']['observedGeneration'] = 3

    def test_old_available_replica_is_not_current_rollout_success(self):
        self.assertFalse(current_rollout(self.fault, self.image))
        for change in [{'observedGeneration': 2}, {'updatedReplicas': 0},
                       {'readyReplicas': 0}, {'replicas': 2}, {'unavailableReplicas': 1}]:
            with self.subTest(change=change):
                deployment = deepcopy(self.repaired)
                deployment['status'].update(change)
                self.assertFalse(current_rollout(deployment, self.image))

    def test_repair_requires_same_uid_and_later_generation(self):
        self.assertTrue(repair_observed(self.initial, self.fault, self.repaired, self.image))
        recreated = deepcopy(self.repaired)
        recreated['metadata']['uid'] = 'replacement'
        self.assertFalse(repair_observed(self.initial, self.fault, recreated, self.image))
        stale = deepcopy(self.repaired)
        stale['metadata']['generation'] = 2
        self.assertFalse(repair_observed(self.initial, self.fault, stale, self.image))
        unproven_fault = deepcopy(self.fault)
        unproven_fault['spec']['template']['spec']['containers'][0]['image'] = self.image
        self.assertFalse(repair_observed(self.initial, unproven_fault, self.repaired, self.image))

    def test_unreviewed_harness_is_not_executed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'harness.py'
            path.write_text('raise AssertionError("must not execute")')
            with self.assertRaisesRegex(ValueError, 'digest differs'):
                load_feasibility(path)
