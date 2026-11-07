from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from scripts.compile_bundle import (
    load_source, compile_bundle, canonical, digest, write_bundle, verify_bundle,
    check_references, release_files,
)
from scripts.publish_bundle import publish, verify_source

ROOT = Path(__file__).resolve().parents[1]


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.catalog = load_source(ROOT / 'fixtures/authoring/catalog.yaml')
        self.cases = json.loads((ROOT / 'fixtures/authoring/assessment-cases.json').read_text())
        self.commit = 'a' * 40

    def build(self, release=False):
        return compile_bundle(self.catalog, self.cases, self.commit, release)

    def production(self):
        # Synthetic non-lab catalog for release-path unit tests only.
        self.catalog['entities'] = [e for e in self.catalog['entities'] if e['id'] != 'exercise.lab']
        self.cases.pop('exercise.lab')
        names = {'fixture.choice': 'choice.exact', 'fixture.order': 'order.exact',
                 'fixture.command': 'command.literal'}
        for entity in self.catalog['entities']:
            if entity['kind'] == 'lesson':
                entity['exercise_ids'].remove('exercise.lab')
            if entity['kind'] == 'exercise':
                assessment = entity['assessment']
                assessment['evaluator'] = names[assessment['evaluator']]

    def test_markdown_and_determinism(self):
        lesson = next(e for e in self.catalog['entities'] if e['kind'] == 'lesson')
        self.assertEqual('Pods expose workload state.\n', lesson['explanation_markdown'])
        original = deepcopy(self.catalog)
        files = self.build()
        self.assertEqual(files, self.build())
        self.assertEqual(original, self.catalog)
        manifest = json.loads(files['manifest.json'])
        self.assertEqual(5, len(manifest['evaluator_requirements']))
        self.assertEqual(self.commit, manifest['source_commit'])
        self.assertFalse(manifest['release_eligible'])

    def test_authoring_rejects_duplicate_keys_tags_and_path_escape(self):
        for source in ('a: 1\na: 2', 'a: !!python/object:builtins.str {}',
                       'a: !markdown ../outside.md', 'a: !markdown /tmp/outside.md',
                       'a: !markdown file.txt'):
            with self.subTest(source=source), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / 'catalog.yaml'
                path.write_text(source)
                with self.assertRaises(Exception):
                    load_source(path)

    def test_markdown_symlink_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'source').mkdir()
            (root / 'outside.md').write_text('outside')
            (root / 'source/link.md').symlink_to(root / 'outside.md')
            path = root / 'source/catalog.yaml'
            path.write_text('text: !markdown link.md')
            with self.assertRaisesRegex(ValueError, 'escapes'):
                load_source(path)

    def test_missing_markdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'catalog.yaml'
            path.write_text('text: !markdown missing.md')
            with self.assertRaises(FileNotFoundError):
                load_source(path)

    def test_schema_errors_block_build(self):
        self.catalog['entities'].append({**self.catalog['entities'][0], 'revision': 2})
        with self.assertRaisesRegex(ValueError, 'duplicate ID'):
            self.build()

    def test_assessment_cases_must_pass_and_cover_both_outcomes(self):
        self.cases['exercise.choice'][0]['expected'] = False
        with self.assertRaisesRegex(ValueError, 'outcome mismatch'):
            self.build()
        self.cases['exercise.choice'] = [{'answer': 'pods', 'expected': True}]
        with self.assertRaisesRegex(ValueError, 'positive and negative'):
            self.build()
        self.cases.pop('exercise.choice')
        with self.assertRaisesRegex(ValueError, 'every exercise'):
            self.build()

    def test_unknown_evaluator_and_invalid_lab_parameters(self):
        lab = next(e for e in self.catalog['entities'] if e['id'] == 'exercise.lab')
        lab['assessment']['checks'][0]['parameters']['namespace'] = 'other-learner'
        with self.assertRaises(Exception):
            self.build()
        lab['assessment']['checks'][0]['parameters'].pop('namespace')
        lab['assessment']['evaluator_version'] = 99
        with self.assertRaisesRegex(ValueError, 'unsupported evaluator'):
            self.build()

    def test_fixtures_cannot_be_released(self):
        with self.assertRaisesRegex(ValueError, 'fixture evaluator'):
            self.build(release=True)
        self.production()
        self.assertTrue(json.loads(self.build(release=True)['manifest.json'])['release_eligible'])

    def test_actual_bytes_exclude_answers_and_parameters(self):
        files = self.build()
        public = json.loads(files['learner.json'])
        for entity in public['entities']:
            if entity['kind'] == 'exercise':
                self.assertEqual(['hint.resource'], entity['hint_ids'])
                for key in ('assessment', 'hints', 'environment_profile'):
                    self.assertNotIn(key, entity)
        for key in ('correct_option_id', 'correct_order', 'accepted_commands',
                    'parameters', 'setup_profile', 'reveal_markdown'):
            self.assertNotIn(('"' + key + '"').encode(), files['learner.json'])
            self.assertIn(('"' + key + '"').encode(), files['assessment.json'])

    def test_integrity_and_exclusive_version_directory(self):
        files = self.build()
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / '0.1.0'
            write_bundle(files, directory)
            sha = digest(files['manifest.json'])
            verify_bundle(directory, sha)
            with self.assertRaises(FileExistsError):
                write_bundle(files, directory)
            with self.assertRaisesRegex(ValueError, 'manifest hash'):
                verify_bundle(directory, '0' * 64)
            (directory / 'learner.json').write_bytes(files['assessment.json'])
            with self.assertRaisesRegex(ValueError, 'integrity'):
                verify_bundle(directory, sha)

    def test_manifest_cannot_bless_answer_leak(self):
        files = self.build()
        files['learner.json'] = files['assessment.json']
        manifest = json.loads(files['manifest.json'])
        manifest['artifacts']['learner.json'].update(
            sha256=digest(files['learner.json']), bytes=len(files['learner.json']))
        files['manifest.json'] = canonical(manifest)
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / 'bundle'
            write_bundle(files, directory)
            with self.assertRaisesRegex(ValueError, 'safe projection'):
                verify_bundle(directory, digest(files['manifest.json']))

    def test_reference_http_failure_and_insecure_redirect(self):
        response = MagicMock()
        response.__enter__.return_value = response
        response.status = 200
        response.geturl.return_value = 'https://docs.redhat.com/test'
        opener = MagicMock(return_value=response)
        self.assertEqual(1, len(check_references(self.catalog, opener)))
        response.status = 404
        with self.assertRaises(ValueError):
            check_references(self.catalog, opener)
        response.status = 200
        response.geturl.return_value = 'http://example.com'
        with self.assertRaises(ValueError):
            check_references(self.catalog, opener)

    @patch('scripts.publish_bundle.verify_source')
    def test_publication_refuses_fixture_and_existing_release(self, verify_source):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / 'fixture'
            files = self.build()
            write_bundle(files, directory)
            with self.assertRaisesRegex(ValueError, 'development bundles'):
                publish(directory, digest(files['manifest.json']))
            self.production()
            directory = Path(tmp) / 'release'
            files = self.build(release=True)
            write_bundle(files, directory)
            with patch('scripts.publish_bundle.gh', side_effect=[
                    '{"enabled":true}', '[[{"tag_name":"content-v0.1.0"}]]']) as gh:
                with self.assertRaisesRegex(ValueError, 'already exists'):
                    publish(directory, digest(files['manifest.json']))
                self.assertEqual(2, gh.call_count)

    def test_release_requires_clean_tracked_inputs(self):
        source = ROOT / 'fixtures/authoring/catalog.yaml'
        cases = source.with_name('assessment-cases.json')
        with patch('scripts.compile_bundle.subprocess.check_output', return_value=' M source'):
            with self.assertRaisesRegex(ValueError, 'clean checkout'):
                release_files(source, cases)
        with patch('scripts.compile_bundle.subprocess.check_output', return_value=''), \
                patch('scripts.compile_bundle.tracked', side_effect=ValueError('not tracked')):
            with self.assertRaisesRegex(ValueError, 'not tracked'):
                release_files(source, cases)

    def test_publish_rebuilds_and_compares_every_artifact(self):
        files = self.build()
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / 'bundle'
            write_bundle(files, directory)
            with patch('scripts.publish_bundle.release_files', return_value=(self.catalog, files)):
                verify_source(directory, '0.1.0')
                (directory / 'manifest.json').write_text('{}')
                with self.assertRaisesRegex(ValueError, 'differs'):
                    verify_source(directory, '0.1.0')

    @patch('scripts.publish_bundle.verify_source')
    def test_publish_blocks_disabled_setting_existing_tag_unmerged_source(self, verify_source):
        self.production()
        files = self.build(release=True)
        failures = [
            (['{"enabled":false}'], 'immutability'),
            (['{"enabled":true}', '[[]]', '[{"ref":"refs/tags/content-v0.1.0"}]'], 'tag already'),
            (['{"enabled":true}', '[[]]', '[]', '{"status":"diverged"}'], 'not on main'),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / 'release'
            write_bundle(files, directory)
            for responses, error in failures:
                with self.subTest(error=error), patch('scripts.publish_bundle.gh', side_effect=responses) as gh:
                    with self.assertRaisesRegex(ValueError, error):
                        publish(directory, digest(files['manifest.json']))
                    self.assertTrue(all(c.args[0] == 'api' for c in gh.call_args_list))

    @patch('scripts.publish_bundle.verify_source')
    def test_publication_draft_upload_then_immutable_publish(self, verify_source):
        self.production()
        files = self.build(release=True)
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / 'release'
            write_bundle(files, directory)
            with patch('scripts.publish_bundle.gh', side_effect=[
                    '{"enabled":true}', '[[]]', '[]', '{"status":"ahead"}', '', '', '',
                    '{"immutable":true,"draft":false,"html_url":"https://example.com/release"}']) as gh:
                publish(directory, digest(files['manifest.json']))
                self.assertIn('/git/refs', gh.call_args_list[4].args[3])
                create = gh.call_args_list[5].args
                self.assertEqual(('release', 'create', 'content-v0.1.0'), create[:3])
                self.assertIn('--draft', create)
                self.assertNotIn('--clobber', create)
                self.assertEqual(('release', 'edit'), gh.call_args_list[6].args[:2])


if __name__ == '__main__':
    unittest.main()
