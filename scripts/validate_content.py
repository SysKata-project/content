"""Validate catalog structure and cross-entity invariants; never execute commands."""
import argparse
from copy import deepcopy
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / 'schemas/1.0.0/catalog.schema.json').read_text())
Draft202012Validator.check_schema(SCHEMA)
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())


def validate(catalog):
    errors = [f'{list(e.path)}: {e.message}' for e in VALIDATOR.iter_errors(catalog)]
    if errors:
        return errors
    entities = catalog['entities']
    by_id = {}
    objectives = {}
    for e in entities:
        if e['id'] in by_id:
            errors.append(f"duplicate ID: {e['id']}")
        by_id[e['id']] = e
        for o in e.get('objectives', []):
            if o['id'] in objectives:
                errors.append(f"duplicate objective ID: {o['id']}")
            objectives[o['id']] = o
    if set(objectives) & set(by_id):
        errors.append('objective and entity IDs overlap')

    def links(owner, values, kind):
        for value in values:
            if value not in by_id or by_id[value]['kind'] != kind:
                errors.append(f'{owner}: broken {kind} reference {value}')

    for e in entities:
        key = e['id']
        links(key, e.get('prerequisites', []), e['kind'])
        links(key, e.get('unit_ids', []), 'unit')
        links(key, e.get('lesson_ids', []), 'lesson')
        links(key, e.get('exercise_ids', []), 'exercise')
        links(key, e.get('skill_ids', []), 'skill')
        links(key, e.get('source', {}).get('reference_ids', []), 'reference')
        for o in e.get('objectives', []):
            links(key, o['skill_ids'], 'skill')
        for oid in e.get('objective_ids', []):
            if oid not in objectives:
                errors.append(f'{key}: broken objective reference {oid}')
            elif not set(objectives[oid]['skill_ids']) <= set(e['skill_ids']):
                errors.append(f'{key}: objective skills are not covered')
        for field in ('options', 'steps', 'hints'):
            values = [v['id'] for v in e.get(field, [])]
            if len(set(values)) != len(values):
                errors.append(f'{key}: duplicate {field} ID')
        assessment = e.get('assessment', {})
        for feedback in assessment.get('feedback', []):
            links(key, feedback['reference_ids'], 'reference')
        if e.get('type') == 'single_choice':
            if assessment['correct_option_id'] not in {o['id'] for o in e['options']}:
                errors.append(f'{key}: unknown correct option')
        if e.get('type') == 'command_order':
            if set(assessment['correct_order']) != {o['id'] for o in e['steps']}:
                errors.append(f'{key}: answer must be a permutation of steps')
        if e.get('type') == 'command_entry':
            for command in assessment['accepted_commands']:
                if normalize_command(command) is None:
                    errors.append(f'{key}: accepted command must be a single line without controls')
        if e.get('type') == 'lab_task':
            criteria = [c['criterion_id'] for c in assessment['checks']]
            if len(criteria) != len(set(criteria)):
                errors.append(f'{key}: duplicate lab criterion')
            if set(criteria) != {f['criterion_id'] for f in assessment['feedback']}:
                errors.append(f'{key}: lab feedback must cover all checks')
        if e['kind'] == 'lesson':
            owned = {o['id'] for o in e['objectives']}
            covered = set()
            for xid in e['exercise_ids']:
                exercise = by_id.get(xid, {})
                targets = set(exercise.get('objective_ids', []))
                covered |= targets
                if not targets <= owned:
                    errors.append(f'{key}: exercise targets another lesson objective')
            if not owned <= covered:
                errors.append(f'{key}: uncovered objective')
    # Iterative DFS avoids recursion failure on long prerequisite chains.
    done = set()
    for start in by_id:
        stack = [(start, False)]
        active = set()
        while stack:
            node, leaving = stack.pop()
            if leaving:
                active.discard(node)
                done.add(node)
            elif node in active:
                errors.append(f'prerequisite cycle: {node}')
            elif node not in done and node in by_id:
                active.add(node)
                stack.append((node, True))
                stack.extend((p, False) for p in by_id[node].get('prerequisites', []))
    return errors


def normalize_command(command):
    """literal-command-v1: trim outside ASCII spaces only; preserve shell syntax."""
    if any(ord(c) < 32 or ord(c) == 127 for c in command):
        return None
    return command.strip(' ') or None


def command_matches(command, accepted):
    normalized = normalize_command(command)
    return normalized is not None and normalized in {
        normalize_command(candidate) for candidate in accepted
    }


PUBLIC_FIELDS = {
    'reference': ('title', 'url', 'baseline', 'reviewed_on'),
    'skill': ('title', 'description', 'prerequisites', 'source'),
    'journey': ('title', 'locale', 'prerequisites', 'unit_ids', 'source', 'runtime'),
    'unit': ('title', 'prerequisites', 'lesson_ids', 'source'),
    'lesson': ('title', 'prerequisites', 'objectives', 'exercise_ids',
               'estimated_minutes', 'explanation_markdown', 'review_prompt', 'source'),
    'exercise': ('type', 'skill_ids', 'objective_ids', 'prompt', 'source',
                 'options', 'steps', 'runtime', 'reset_behavior'),
}


def projections(catalog):
    errors = validate(catalog)
    if errors:
        raise ValueError('\n'.join(errors))
    learner = {k: catalog[k] for k in ('schema_version', 'bundle_version')}
    learner['entities'] = []
    for e in catalog['entities']:
        fields = ('kind', 'id', 'revision') + PUBLIC_FIELDS[e['kind']]
        public = {k: deepcopy(e[k]) for k in fields if k in e}
        if e['kind'] == 'exercise':
            public['hint_ids'] = [h['id'] for h in e['hints']]
        learner['entities'].append(public)
    # Trusted projection retains hint/reveal material for tracked delivery by API.
    return learner, deepcopy(catalog)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalog', type=Path)
    args = parser.parse_args()
    try:
        errors = validate(json.loads(args.catalog.read_text()))
    except (OSError, ValueError) as exc:
        parser.exit(1, f'{exc}\n')
    if errors:
        parser.exit(1, '\n'.join(errors) + '\n')
    print(f'Valid: {args.catalog}')


if __name__ == '__main__':
    main()
