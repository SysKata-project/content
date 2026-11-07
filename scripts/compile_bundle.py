"""Compile YAML/Markdown into deterministic, separately scoped JSON artifacts."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import urllib.request
from urllib.parse import urlparse

import yaml

try:
    from .validate_content import projections, command_matches
except ImportError:
    from validate_content import projections, command_matches


class SourceLoader(yaml.SafeLoader):
    """Reject duplicate keys; keep ISO dates as strings for JSON Schema."""


SourceLoader.yaml_implicit_resolvers = {
    key: [(tag, regex) for tag, regex in values
          if tag != 'tag:yaml.org,2002:timestamp']
    for key, values in SourceLoader.yaml_implicit_resolvers.items()
}


def mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=True)
        if not isinstance(key, str) or key in result:
            raise ValueError('YAML requires unique string keys')
        result[key] = loader.construct_object(value_node, deep=True)
    return result


SourceLoader.add_constructor('tag:yaml.org,2002:map', mapping)


def canonical(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False,
                       allow_nan=False, separators=(',', ':')) + '\n').encode('utf-8')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def confined(root, name):
    if not isinstance(name, str) or Path(name).is_absolute():
        raise ValueError('source paths must be relative')
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('source path escapes authoring directory')
    return path


def load_source(path, require_tracked=False):
    """A catalog YAML with !markdown scalar paths relative to its directory."""
    root = path.resolve().parent
    if require_tracked:
        tracked(path)

    class Loader(SourceLoader):
        pass

    def markdown(loader, node):
        target = confined(root, loader.construct_scalar(node))
        if target.suffix != '.md':
            raise ValueError('!markdown requires a .md file')
        if require_tracked:
            tracked(target)
        return target.read_text(encoding='utf-8')

    Loader.add_constructor('!markdown', markdown)
    return yaml.load(path.read_text(encoding='utf-8'), Loader=Loader)


# These names identify exact local grading semantics. Production lab adapters
# belong to labs #3; fixture adapters must never pass the release gate.
ADAPTERS = {
    ('choice.exact', 1): 'single_choice',
    ('order.exact', 1): 'command_order',
    ('command.literal', 1): 'command_entry',
    ('fixture.choice', 1): 'single_choice',
    ('fixture.order', 1): 'command_order',
    ('fixture.command', 1): 'command_entry',
    ('fixture.lab', 1): 'lab_task',
}
POD_PARAMETERS = {
    'type': 'object', 'additionalProperties': False,
    'required': ['pod', 'ready'],
    'properties': {'pod': {'type': 'string', 'minLength': 1},
                   'ready': {'type': 'boolean'}},
}


def evaluate(exercise, answer):
    assessment = exercise['assessment']
    kind = exercise['type']
    if kind == 'single_choice':
        return isinstance(answer, str) and answer == assessment['correct_option_id']
    if kind == 'command_order':
        return isinstance(answer, list) and answer == assessment['correct_order']
    if kind == 'command_entry':
        return isinstance(answer, str) and command_matches(answer, assessment['accepted_commands'])
    # A pure fixture adapter: observations are supplied data, never live evidence.
    return isinstance(answer, dict) and all(
        answer.get(check['criterion_id']) == check['parameters']
        for check in assessment['checks'])


def validate_assessments(catalog, cases, release=False):
    from jsonschema import Draft202012Validator

    if not isinstance(cases, dict):
        raise ValueError('assessment fixtures must map exercise IDs to cases')
    exercises = {e['id']: e for e in catalog['entities'] if e['kind'] == 'exercise'}
    if set(cases) != set(exercises):
        raise ValueError('assessment fixtures must cover exactly every exercise')
    requirements = set()
    for eid, exercise in exercises.items():
        assessment = exercise['assessment']
        capability = (assessment['evaluator'], assessment['evaluator_version'])
        if ADAPTERS.get(capability) != exercise['type']:
            raise ValueError(f'{eid}: unsupported evaluator or exercise type')
        if release and capability[0].startswith('fixture.'):
            raise ValueError(f'{eid}: fixture evaluator cannot be released')
        requirements.add(capability)
        if exercise['type'] == 'lab_task':
            if release:
                # Fail closed until a real versioned lab adapter and its evidence
                # validator are integrated; tested_versions alone proves nothing.
                raise ValueError(f'{eid}: production lab adapter/evidence not integrated')
            if (exercise['environment_profile'], assessment['setup_profile']) != (
                    'fixture.project', 'fixture.pods'):
                raise ValueError(f'{eid}: unsupported lab profiles')
            for check in assessment['checks']:
                key = (check['evaluator'], check['evaluator_version'])
                if key != ('fixture.pod-ready', 1):
                    raise ValueError(f'{eid}: unsupported lab check')
                Draft202012Validator(POD_PARAMETERS).validate(check['parameters'])
                requirements.add(key)
        rows = cases[eid]
        if not isinstance(rows, list) or not rows:
            raise ValueError(f'{eid}: expected nonempty fixture cases')
        outcomes = set()
        for case in rows:
            if (not isinstance(case, dict) or set(case) != {'answer', 'expected'}
                    or type(case['expected']) is not bool):
                raise ValueError(f'{eid}: invalid assessment fixture')
            outcomes.add(case['expected'])
            if evaluate(exercise, case['answer']) != case['expected']:
                raise ValueError(f'{eid}: assessment fixture outcome mismatch')
        if outcomes != {True, False}:
            raise ValueError(f'{eid}: positive and negative cases are required')
    return [{'evaluator': name, 'version': version} for name, version in sorted(requirements)]


def check_references(catalog, opener=None):
    """Fail closed on HTTP errors; HTTPS GET avoids HEAD-incompatible doc sites."""
    opener = opener or urllib.request.urlopen
    urls = sorted({e['url'] for e in catalog['entities'] if e['kind'] == 'reference'})
    for url in urls:
        parsed = urlparse(url)
        if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError('documentation references require credential-free HTTPS URLs')
        request = urllib.request.Request(url, headers={'User-Agent': 'SysKata-content-validator/1'})
        with opener(request, timeout=30) as response:
            if response.status != 200 or urlparse(response.geturl()).scheme != 'https':
                raise ValueError(f'documentation reference unavailable: {url}')
            response.read(1)
    return urls


def compile_bundle(catalog, cases, source_commit, release=False):
    if not re.fullmatch(r'[0-9a-f]{40}', source_commit):
        raise ValueError('source commit must be a full Git SHA-1')
    learner, assessment = projections(catalog)
    requirements = validate_assessments(catalog, cases, release)
    files = {'learner.json': canonical(learner), 'assessment.json': canonical(assessment)}
    manifest = {
        'manifest_version': 1, 'schema_version': catalog['schema_version'],
        'bundle_version': catalog['bundle_version'], 'source_commit': source_commit,
        'release_eligible': release,
        'evaluator_requirements': requirements,
        'assessment_fixtures_sha256': digest(canonical(cases)),
        'artifacts': {name: {'sha256': digest(data), 'bytes': len(data),
                            'audience': 'learner' if name == 'learner.json' else 'trusted'}
                      for name, data in files.items()},
    }
    files['manifest.json'] = canonical(manifest)
    return files


def write_bundle(files, directory):
    # Exclusive creation prevents replacing even identical versions by accident.
    directory.mkdir(parents=True, exist_ok=False)
    for name, data in files.items():
        (directory / name).write_bytes(data)


def verify_bundle(directory, expected_manifest_hash):
    manifest_bytes = (directory / 'manifest.json').read_bytes()
    if digest(manifest_bytes) != expected_manifest_hash:
        raise ValueError('manifest hash does not match the pinned release')
    manifest = json.loads(manifest_bytes)
    if manifest['manifest_version'] != 1 or set(manifest['artifacts']) != {
            'learner.json', 'assessment.json'}:
        raise ValueError('unsupported manifest')
    for name, info in manifest['artifacts'].items():
        data = (directory / name).read_bytes()
        if digest(data) != info['sha256'] or len(data) != info['bytes']:
            raise ValueError(f'artifact integrity failure: {name}')
    trusted = json.loads((directory / 'assessment.json').read_bytes())
    learner, _ = projections(trusted)
    if canonical(learner) != (directory / 'learner.json').read_bytes():
        raise ValueError('learner artifact does not match safe projection')
    for field in ('schema_version', 'bundle_version'):
        if trusted[field] != manifest[field]:
            raise ValueError(f'manifest {field} mismatch')
    return manifest


def tracked(path):
    subprocess.run(['git', 'ls-files', '--error-unmatch', str(path.resolve())],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def release_files(source, cases_path):
    if subprocess.check_output(
            ['git', 'status', '--porcelain', '--untracked-files=all'], text=True).strip():
        raise ValueError('release builds require a clean checkout')
    tracked(cases_path)
    catalog = load_source(source, require_tracked=True)
    cases = json.loads(cases_path.read_text())
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    files = compile_bundle(catalog, cases, commit, release=True)
    check_references(catalog)
    return catalog, files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    build = commands.add_parser('build')
    build.add_argument('source', type=Path)
    build.add_argument('--cases', required=True, type=Path)
    build.add_argument('--output', required=True, type=Path)
    build.add_argument('--release', action='store_true')
    build.add_argument('--check-links', action='store_true')
    verify = commands.add_parser('verify')
    verify.add_argument('directory', type=Path)
    verify.add_argument('--manifest-sha256', required=True)
    args = parser.parse_args()
    try:
        if args.command == 'verify':
            verify_bundle(args.directory, args.manifest_sha256)
        else:
            commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
            if args.release:
                catalog, files = release_files(args.source, args.cases)
            else:
                catalog = load_source(args.source)
                cases = json.loads(args.cases.read_text())
                files = compile_bundle(catalog, cases, commit)
                if args.check_links:
                    check_references(catalog)
            directory = args.output / catalog['bundle_version']
            write_bundle(files, directory)
            print(f'{directory}: manifest SHA-256 {digest(files["manifest.json"])}')
    except (OSError, ValueError, yaml.YAMLError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f'{exc}\n')


if __name__ == '__main__':
    main()
