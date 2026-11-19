"""Operator-run checkpoint B proof, never a production evaluator."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import signal
import subprocess
import time

import yaml

try:
    from .validate_foundations import load_feasibility, current_rollout, FEASIBILITY_SHA256
except ImportError:
    from validate_foundations import load_feasibility, current_rollout, FEASIBILITY_SHA256

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / 'drafts/0.3.0'


def authorization_denied(result):
    """Connectivity/authentication failures must not pass an authorization check."""
    return result.returncode != 0 and 'Forbidden' in result.stderr


def quota_denied(result):
    return (authorization_denied(result) and 'exceeded quota: exercise-budget' in result.stderr)


def manifest_matches(actual, desired):
    """Check desired workload fields, allowing server-added defaults."""
    def contains(value, expected):
        if isinstance(expected, dict):
            return isinstance(value, dict) and all(k in value and contains(value[k], v)
                                                  for k, v in expected.items())
        if isinstance(expected, list):
            return isinstance(value, list) and len(value) == len(expected) and all(
                contains(v, e) for v, e in zip(value, expected))
        return value == expected
    image = desired['spec']['template']['spec']['containers'][0]['image']
    return contains(actual['spec'], desired['spec']) and current_rollout(actual, image)


def quota_matches(quota):
    return (quota['spec'].get('hard') == {'pods': '1'}
            and quota.get('status', {}).get('hard') == {'pods': '1'}
            and quota.get('status', {}).get('used', {}).get('pods') == '1')


def build_validation(module):
    class Administration(module.Validation):
        def __init__(self, config, output):
            super().__init__(config, output, 1)
            self.desired = yaml.safe_load((DRAFT / 'checkpoint/web.yaml').read_text())
            paths = [Path(__file__), ROOT / 'scripts/validate_foundations.py',
                     *sorted((DRAFT / 'checkpoint').glob('*.yaml')),
                     DRAFT / 'checkpoint/scenario-cases.json']
            self.report.update(checkpoint_id='checkpoint.oc-administration', content_revision=1,
                               proof_version=1, production_evaluator=False,
                               feasibility_sha256=FEASIBILITY_SHA256,
                               source_commit=subprocess.check_output(
                                   ['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
                               inputs_sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                             for p in paths})

        def command(self, label, *args, data=None, config=None):
            result = self.oc(*args, data=data, config=config)
            self.check(label, result.returncode == 0)
            return result

        def wait_for(self, predicate, seconds=90):
            until = time.monotonic() + seconds
            while time.monotonic() < until:
                if predicate():
                    return True
                time.sleep(2)
            return False

        def apply(self, obj):
            self.command('learner applies ' + obj['kind'], 'apply', '-f', '-', '-n', self.ns,
                         data=obj, config=self.client)

        def deployment(self):
            return self.get('get', 'deployment', 'web', '-n', self.ns)

        def access(self, label, expected):
            allowed = self.oc('get', 'pods', '-n', self.ns, config=self.reader)
            self.check(label, allowed.returncode == 0 if expected else authorization_denied(allowed))

        def reader_denials(self):
            for label, args in [
                ('pod deletion', ['delete', 'pod', 'nonexistent-proof-target', '-n', self.ns]),
                ('secret read', ['get', 'secrets', '-n', self.ns]),
                ('foreign pod read', ['get', 'pods', '-n', self.foreign]),
            ]:
                self.check('supplied identity denied ' + label,
                           authorization_denied(self.oc(*args, config=self.reader)))

        def execute(self, directory):
            version = self.get('get', 'clusterversion', 'version')['status']['desired']['version']
            self.report['openshift_version'] = version
            self.check('curriculum minor version compatible', version.startswith('4.22.'))
            self.report['limitations'] = [
                'Scoped curriculum proof, not production evaluator or lifecycle integration',
                'API generation, reward deduplication, checkpoint unlock and TTL enforcement not tested',
                'Infrastructure failure classification tested offline only',
                'Replacement cluster must also pass the full feasibility isolation proof',
            ]
            for obj in module.admission_resources(self.run_id):
                self.admission.append((obj['kind'], obj['metadata']['name']))
                self.create(obj)
            self.ns, self.foreign = self.run_id + '-administration', self.run_id + '-foreign'
            outer = {'requests.cpu': '500m', 'requests.memory': '512Mi',
                     'limits.cpu': '1', 'limits.memory': '1Gi', 'pods': '4'}
            for ns in [self.ns, self.foreign]:
                self.namespaces.append(ns)
                self.create({'apiVersion': 'v1', 'kind': 'Namespace',
                             'metadata': {'name': ns, 'labels': {module.LABEL: self.run_id}}})
                self.create(module.resource('ResourceQuota', 'outer-budget', {'hard': outer}), ns)
                for obj in module.policies():
                    self.create(obj, ns)
            for name in ['learner', 'supplied-reader']:
                self.create(module.resource('ServiceAccount', name, automountServiceAccountToken=False), self.ns)
            # Use the reviewed non-escalating feasibility permissions, without exec/Routes/Services.
            rules = [r for r in module.learner_rules()
                     if r['resources'] not in (['pods/exec'], ['routes'], ['pods', 'services'])]
            rules.append({'apiGroups': [''], 'resources': ['pods'],
                          'verbs': ['get', 'list', 'watch', 'create', 'update', 'patch', 'delete']})
            self.create(module.resource('Role', 'learner', api='rbac.authorization.k8s.io/v1', rules=rules), self.ns)
            self.create(module.resource('RoleBinding', 'learner', api='rbac.authorization.k8s.io/v1',
                subjects=[{'kind': 'ServiceAccount', 'name': 'learner', 'namespace': self.ns}],
                roleRef={'apiGroup': 'rbac.authorization.k8s.io', 'kind': 'Role', 'name': 'learner'}), self.ns)
            self.client, _ = self.token_config(self.ns, 'learner', directory)
            self.reader, _ = self.token_config(self.ns, 'supplied-reader', directory)
            for verb, target in [('get', 'secrets'), ('get', 'nodes'), ('create', 'serviceaccounts/token'),
                                 ('patch', 'networkpolicies'), ('patch', 'resourcequotas/outer-budget'),
                                 ('impersonate', 'users'), ('escalate', 'roles')]:
                self.check('learner denied ' + verb + ' ' + target,
                           not self.can(self.client, self.ns, verb, target))
            self.check('learner denied cross-project read', authorization_denied(
                self.oc('get', 'pods', '-n', self.foreign, config=self.client)))
            self.access('unbound supplied identity denied pod read', False)
            for generation in [1, 2]:
                # The first pass uses one rule; the alternate splits equivalent verbs.
                self.apply(self.desired)
                self.command('learner observes rollout', 'rollout', 'status', 'deployment/web',
                             '-n', self.ns, '--timeout=120s', config=self.client)
                self.check('manifest desired and observed state', self.wait_for(
                    lambda: manifest_matches(self.deployment(), self.desired)))
                original_uid = self.deployment()['metadata']['uid']
                self.apply(self.desired)
                self.check('reapply preserves workload identity', self.deployment()['metadata']['uid'] == original_uid)
                wrong = deepcopy(self.desired)
                wrong['spec']['template']['metadata']['labels']['exercise'] = 'wrong'
                self.apply(wrong)
                self.check('wrong declared label rejected', not manifest_matches(self.deployment(), self.desired))
                self.apply(self.desired)
                self.check('correct manifest restored', self.wait_for(
                    lambda: manifest_matches(self.deployment(), self.desired)))
                role = yaml.safe_load((DRAFT / 'checkpoint/reader-role.yaml').read_text())
                if generation == 2:
                    role['rules'] = [{'apiGroups': [''], 'resources': ['pods'], 'verbs': [v]}
                                     for v in ['list', 'get']]
                self.apply(role)
                binding = yaml.safe_load((DRAFT / 'checkpoint/reader-binding.yaml').read_text())
                binding['subjects'][0]['namespace'] = self.ns
                wrong_binding = deepcopy(binding)
                wrong_binding['subjects'][0]['name'] = 'unassigned-reader'
                self.apply(wrong_binding)
                self.access('wrong subject does not grant supplied identity access', False)
                self.apply(binding)
                self.check('supplied identity gains pod list', self.wait_for(
                    lambda: self.oc('get', 'pods', '-n', self.ns, config=self.reader).returncode == 0))
                pod_name = self.get('get', 'pods', '-n', self.ns)['items'][0]['metadata']['name']
                self.command('supplied identity can get named pod', 'get', 'pod', pod_name,
                             '-n', self.ns, config=self.reader)
                self.reader_denials()
                broad = deepcopy(role)
                broad['rules'][0]['verbs'].append('delete')
                self.apply(broad)
                self.check('overbroad grant detected', self.wait_for(
                    lambda: self.can(self.reader, self.ns, 'delete', 'pods')))
                self.apply(role)
                self.check('delete grant removed', self.wait_for(
                    lambda: not self.can(self.reader, self.ns, 'delete', 'pods')))
                self.reader_denials()
                escalation = deepcopy(binding)
                escalation['metadata']['name'] = 'escape'
                escalation['roleRef'] = {'apiGroup': 'rbac.authorization.k8s.io',
                                        'kind': 'ClusterRole', 'name': 'cluster-admin'}
                self.check('cluster-admin binding rejected', self.create(escalation, self.ns, self.client, forbidden=True))
                quota = yaml.safe_load((DRAFT / 'checkpoint/exercise-budget.yaml').read_text())
                self.apply(quota)
                self.check('exercise quota accounted one pod', self.wait_for(
                    lambda: quota_matches(self.get('get', 'resourcequota', 'exercise-budget', '-n', self.ns))))
                probe = module.resource('Pod', 'over-budget', deepcopy(self.desired['spec']['template']['spec']))
                self.check('second pod rejected by exercise quota', quota_denied(
                    self.oc('create', '-f', '-', '-n', self.ns, data=probe, config=self.client)))
                changed = deepcopy(quota)
                changed['spec']['hard']['pods'] = '2'
                self.apply(changed)
                self.check('too-large exercise quota rejected', not quota_matches(
                    self.get('get', 'resourcequota', 'exercise-budget', '-n', self.ns)))
                self.apply(quota)
                self.check('restored quota accounted', self.wait_for(
                    lambda: quota_matches(self.get('get', 'resourcequota', 'exercise-budget', '-n', self.ns))))
                denied = self.oc('patch', 'resourcequota', 'outer-budget', '-n', self.ns,
                                 '--type=merge', '-p', '{"spec":{"hard":{"pods":"100"}}}', config=self.client)
                self.check('outer quota mutation rejected', authorization_denied(denied))
                self.check('outer quota unchanged', self.get('get', 'resourcequota', 'outer-budget', '-n', self.ns)['spec']['hard'] == outer)
                # Operator-only reset: remove exercise limits before workload deletion/recreation.
                for kind, name in [('resourcequota', 'exercise-budget'), ('rolebinding', 'exercise-reader'),
                                   ('role', 'exercise-reader'), ('deployment', 'web')]:
                    self.command('reset deletes ' + kind, 'delete', kind, name, '-n', self.ns,
                                 '--wait=true', '--timeout=60s')
                    result = self.oc('get', kind, name, '-n', self.ns)
                    self.check('reset confirms absence of ' + kind,
                               result.returncode != 0 and 'NotFound' in result.stderr)
                self.check('reset removes workload pods', self.wait_for(
                    lambda: not self.get('get', 'pods', '-n', self.ns)['items']))
                self.check('reset revokes supplied reader access', self.wait_for(
                    lambda: authorization_denied(self.oc('get', 'pods', '-n', self.ns, config=self.reader))))
                self.check('reset retains outer ceiling', self.get(
                    'get', 'resourcequota', 'outer-budget', '-n', self.ns)['spec']['hard'] == outer)
    return Administration


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--feasibility-harness', type=Path, required=True)
    parser.add_argument('--kubeconfig', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    module = load_feasibility(args.feasibility_harness)
    def interrupted(signum, frame):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, interrupted)
    raise SystemExit(0 if build_validation(module)(args.kubeconfig, args.report).run() else 1)


if __name__ == '__main__':
    main()
