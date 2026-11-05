from copy import deepcopy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, FormatChecker
from scripts.validate_content import SCHEMA, validate, projections, command_matches

ROOT = Path(__file__).resolve().parents[1]


class ContentTests(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads((ROOT / 'fixtures/valid/catalog.json').read_text())

    def entity(self, kind):
        return next(e for e in self.catalog['entities'] if e.get('type', e['kind']) == kind)

    def test_catalog(self):
        self.assertEqual([], validate(self.catalog))

    def test_entity_fixtures(self):
        for path in (ROOT / 'fixtures/valid').glob('*.json'):
            if path.stem == 'catalog':
                continue
            schema = {'$ref': '#/$defs/' + path.stem, '$defs': SCHEMA['$defs']}
            validator = Draft202012Validator(schema, format_checker=FormatChecker())
            with self.subTest(kind=path.stem):
                self.assertTrue(validator.is_valid(json.loads(path.read_text())))
                invalid = ROOT / 'fixtures/invalid' / path.name
                self.assertFalse(validator.is_valid(json.loads(invalid.read_text())))

    def test_duplicate_entity(self):
        self.catalog['entities'].append({**self.entity('skill'), 'revision': 2})
        self.assertIn('duplicate ID', '\n'.join(validate(self.catalog)))

    def test_broken_reference(self):
        self.entity('single_choice')['source']['reference_ids'] = ['missing']
        self.assertIn('broken reference reference', '\n'.join(validate(self.catalog)))

    def test_cycle(self):
        self.entity('skill')['prerequisites'] = ['skill.observe']
        self.assertIn('prerequisite cycle', '\n'.join(validate(self.catalog)))

    def test_longer_cycle(self):
        other = deepcopy(self.entity('skill'))
        other.update(id='skill.other', prerequisites=['skill.observe'])
        self.entity('skill')['prerequisites'] = ['skill.other']
        self.catalog['entities'].append(other)
        self.assertIn('prerequisite cycle', '\n'.join(validate(self.catalog)))

    def test_wrong_reference_type(self):
        self.entity('journey')['unit_ids'] = ['skill.observe']
        self.assertIn('broken unit reference', '\n'.join(validate(self.catalog)))

    def test_bad_answers(self):
        self.entity('single_choice')['assessment']['correct_option_id'] = 'missing'
        self.entity('command_order')['assessment']['correct_order'] = ['inspect']
        errors = '\n'.join(validate(self.catalog))
        self.assertIn('unknown correct option', errors)
        self.assertIn('permutation', errors)

    def test_bad_date(self):
        self.entity('reference')['reviewed_on'] = '2026-02-30'
        self.assertTrue(validate(self.catalog))

    def test_unknown_field(self):
        self.entity('lesson')['unexpected'] = True
        self.assertTrue(validate(self.catalog))

    def test_objective_coverage(self):
        self.entity('lesson')['objectives'].append({
            'id': 'objective.extra', 'description': 'Uncovered', 'skill_ids': ['skill.observe']})
        self.assertIn('uncovered objective', '\n'.join(validate(self.catalog)))

    def test_lab_feedback(self):
        self.entity('lab_task')['assessment']['feedback'][0]['criterion_id'] = 'missing'
        self.assertIn('lab feedback', '\n'.join(validate(self.catalog)))

    def test_duplicate_local_ids(self):
        self.entity('single_choice')['options'][1]['id'] = 'pods'
        self.assertIn('duplicate options ID', '\n'.join(validate(self.catalog)))

    def test_projections(self):
        original = deepcopy(self.catalog)
        learner, trusted = projections(self.catalog)
        public = json.dumps(learner)
        for forbidden in ('assessment', 'correct_option_id', 'correct_order',
                          'accepted_commands', 'parameters', 'reveal_markdown',
                          'misconception_code', 'evaluator', 'setup_profile', 'hints'):
            self.assertNotIn('"' + forbidden + '"', public)
        self.assertEqual(original, trusted)
        self.assertEqual(original, self.catalog)
        trusted['entities'].clear()
        self.assertEqual(original, self.catalog)

    def test_invalid_projection_refused(self):
        self.entity('skill')['extra'] = 'do not leak'
        with self.assertRaises(ValueError):
            projections(self.catalog)

    def test_command_semantics(self):
        self.assertTrue(command_matches('  oc get pods  ', ['oc get pods']))
        self.assertTrue(command_matches('oc get pod', ['oc get pods', 'oc get pod']))
        for command in ('OC get pods', 'oc  get pods', 'oc get pods\n',
                        'oc get pods; whoami', 'oc get pods --all-namespaces',
                        'oc get "pods"', 'oc get pods | cat', 'oc get pods\t'):
            with self.subTest(command=command):
                self.assertFalse(command_matches(command, ['oc get pods']))
        self.assertFalse(command_matches('oc label pod x a="b c"', ['oc label pod x a=b c']))


if __name__ == '__main__':
    unittest.main()
