"""Operator-run curriculum proof; not a production evaluator or lifecycle service."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import signal
import subprocess
import time

import yaml

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / 'drafts/0.2.0'
# Reuse the reviewed isolation/credential/cleanup implementation without copying it.
FEASIBILITY_SHA256 = '53fdfe51dcb658265c60e001827e5db01df0c7b068180ca9635568c2edac9534'
FAULT_IMAGE = 'registry.invalid/syskata/deliberate-rollout-fault:v1'


def load_feasibility(path):
    if hashlib.sha256(path.read_bytes()).hexdigest() != FEASIBILITY_SHA256:
        raise ValueError('feasibility harness digest differs from reviewed version')
    spec = importlib.util.spec_from_file_location('syskata_feasibility', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def current_rollout(deployment, image):
    spec, status = deployment['spec'], deployment.get('status', {})
    containers = spec['template']['spec']['containers']
    return (spec['replicas'] == 1 and len(containers) == 1
            and containers[0]['image'] == image
            and status.get('observedGeneration', 0) >= deployment['metadata']['generation']
            and status.get('updatedReplicas', 0) == 1
            and status.get('readyReplicas', 0) == 1
            and status.get('replicas', 0) == 1
            and status.get('unavailableReplicas', 0) == 0)


def repair_observed(initial, fault, repaired, image):
    return (initial['metadata']['uid'] == fault['metadata']['uid'] == repaired['metadata']['uid']
            and initial['metadata']['generation'] < fault['metadata']['generation']
            < repaired['metadata']['generation']
            and fault['spec']['template']['spec']['containers'][0]['image'] == FAULT_IMAGE
            and current_rollout(repaired, image))


def build_validation(module):
    class Foundations(module.Validation):
        def __init__(self, config, output):
            super().__init__(config, output, 1)
            self.workload = yaml.safe_load((DRAFT / 'checkpoint/web.yaml').read_text())
            self.image = self.workload['spec']['template']['spec']['containers'][0]['image']
            self.report.update(checkpoint_id='checkpoint.oc-foundations', content_revision=1,
                               proof_version=1, production_evaluator=False,
                               feasibility_sha256=FEASIBILITY_SHA256,
                               source_commit=subprocess.check_output(
                                   ['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
                               inputs_sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                             for p in [Path(__file__), *sorted((DRAFT / 'checkpoint').glob('*.yaml'))]})

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

        def deployment(self):
            return self.get('get', 'deployment', 'web', '-n', self.ns)

        def patch(self, kind, patch, config=None):
            self.command('patch ' + kind, 'patch', kind, 'web', '-n', self.ns,
                         '--type=merge', '-p', json.dumps(patch), config=config or self.client)

        def rollout(self):
            self.command('learner rollout status', 'rollout', 'status', 'deployment/web',
                         '-n', self.ns, '--timeout=120s', config=self.client)
            self.check('latest rollout fully ready', self.wait_for(
                lambda: current_rollout(self.deployment(), self.image)))

        def backend(self):
            service = self.get('get', 'service', 'web', '-n', self.ns)
            slices = self.get('get', 'endpointslices', '-n', self.ns,
                              '-l', 'kubernetes.io/service-name=web')['items']
            pods = self.get('get', 'pods', '-n', self.ns, '-l', 'app=web')['items']
            ready_uids = {p['metadata']['uid'] for p in pods if any(
                c['type'] == 'Ready' and c['status'] == 'True'
                for c in p.get('status', {}).get('conditions', []))}
            spec = service['spec']
            return (spec.get('type') == 'ClusterIP' and not spec.get('externalIPs')
                    and spec.get('selector') == {'app': 'web'}
                    and any(p['port'] == 8080 and p['targetPort'] == 8080 for p in spec['ports'])
                    and any(any(o.get('uid') == service['metadata']['uid'] for o in s['metadata'].get('ownerReferences', []))
                            and any(e.get('conditions', {}).get('ready') is True
                                    and e.get('targetRef', {}).get('uid') in ready_uids
                                    for e in s.get('endpoints', [])) for s in slices))

        def route(self):
            obj = self.get('get', 'route', 'web', '-n', self.ns)
            spec = obj['spec']
            return (spec['host'] == self.host and spec['to']['name'] == 'web'
                    and spec.get('tls', {}).get('termination') == 'edge'
                    and spec.get('tls', {}).get('insecureEdgeTerminationPolicy') == 'Redirect'
                    and spec.get('port', {}).get('targetPort') == 8080
                    and any(c['type'] == 'Admitted' and c['status'] == 'True'
                            for ingress in obj.get('status', {}).get('ingress', [])
                            for c in ingress.get('conditions', [])))

        def response(self):
            # Do not inherit the API kubeconfig's insecure TLS setting for routes.
            result = subprocess.run(['curl', '--silent', '--show-error', '--fail',
                                     '--max-time', '8', 'https://' + self.host],
                                    capture_output=True, text=True, timeout=12)
            return (result.returncode == 0 and 'Directory listing for /' in result.stdout
                    and '<ul>\n</ul>' in result.stdout)

        def healthy(self):
            self.rollout()
            self.check('Service links ready backend', self.wait_for(self.backend))
            self.check('edge Route admitted with assigned host', self.wait_for(self.route))
            self.check('TLS-verified expected HTTPS response', self.wait_for(self.response))

        def fault_and_repair(self, imperative=False):
            initial = self.deployment()
            fault = yaml.safe_load((DRAFT / 'checkpoint/fault.patch.yaml').read_text())
            self.command('operator injects controlled image fault', 'patch', 'deployment', 'web',
                         '-n', self.ns, '--type=strategic', '-p', json.dumps(fault))
            def pull_failed():
                pods = self.get('get', 'pods', '-n', self.ns)['items']
                return any(any(c.get('state', {}).get('waiting', {}).get('reason')
                               in ('ErrImagePull', 'ImagePullBackOff') for c in p.get('status', {}).get('containerStatuses', []))
                           for p in pods if p['spec']['containers'][0]['image'] == FAULT_IMAGE)
            self.check('controlled image pull failure observed', self.wait_for(pull_failed))
            failed = self.deployment()
            self.check('old replica cannot prove repaired rollout', not current_rollout(failed, self.image))
            self.command('learner reads pod events', 'get', 'events', '-n', self.ns, config=self.client)
            pods = self.get('get', 'pods', '-n', self.ns)['items']
            broken = next(p for p in pods if p['spec']['containers'][0]['image'] == FAULT_IMAGE)
            result = self.command('learner describes failing pod', 'describe', 'pod',
                                  broken['metadata']['name'], '-n', self.ns, config=self.client)
            self.check('learner sees image failure diagnosis', 'Failed' in result.stdout and FAULT_IMAGE in result.stdout)
            if imperative:
                self.command('alternate imperative image repair', 'set', 'image', 'deployment/web',
                             'web=' + self.image, '-n', self.ns, config=self.client)
            else:
                self.command('manifest image repair', 'apply', '-f', '-', '-n', self.ns,
                             data=self.workload, config=self.client)
            self.healthy()
            repaired = self.deployment()
            self.check('trusted UID and generation repair sequence', repair_observed(initial, failed, repaired, self.image),
                       method='imperative' if imperative else 'manifest',
                       generations=[x['metadata']['generation'] for x in (initial, failed, repaired)])

        def execute(self, directory):
            self.report['openshift_version'] = self.get('get', 'clusterversion', 'version')['status']['desired']['version']
            self.check('curriculum minor version compatible', self.report['openshift_version'].startswith('4.22.'))
            for obj in module.admission_resources(self.run_id):
                self.admission.append((obj['kind'], obj['metadata']['name']))
                self.create(obj)
            self.ns = self.run_id + '-foundations'
            self.namespaces.append(self.ns)
            self.create({'apiVersion': 'v1', 'kind': 'Namespace',
                         'metadata': {'name': self.ns, 'labels': {module.LABEL: self.run_id}}})
            self.create(module.resource('ResourceQuota', 'outer-budget', {'hard': {
                'requests.cpu': '500m', 'requests.memory': '512Mi', 'limits.cpu': '1',
                'limits.memory': '1Gi', 'pods': '4'}}), self.ns)
            for obj in module.policies():
                self.create(obj, self.ns)
            self.create(module.resource('ServiceAccount', 'learner', automountServiceAccountToken=False), self.ns)
            # Foundation-specific temporary role: no RBAC/quota/exec mutation permissions.
            rules = [r for r in module.learner_rules() if r['resources'] in (
                ['pods', 'services'], ['pods/log'], ['deployments'], ['routes'])]
            rules += [{'apiGroups': [''], 'resources': ['events', 'endpoints'], 'verbs': ['get', 'list', 'watch']},
                      {'apiGroups': ['apps'], 'resources': ['replicasets'], 'verbs': ['get', 'list', 'watch']}]
            self.create(module.resource('Role', 'learner', api='rbac.authorization.k8s.io/v1', rules=rules), self.ns)
            self.create(module.resource('RoleBinding', 'learner', api='rbac.authorization.k8s.io/v1',
                subjects=[{'kind': 'ServiceAccount', 'name': 'learner', 'namespace': self.ns}],
                roleRef={'apiGroup': 'rbac.authorization.k8s.io', 'kind': 'Role', 'name': 'learner'}), self.ns)
            self.client, _ = self.token_config(self.ns, 'learner', directory)
            for verb, target in [('get', 'secrets'), ('get', 'nodes'), ('create', 'serviceaccounts/token'),
                                 ('patch', 'networkpolicies'), ('patch', 'resourcequotas/outer-budget')]:
                self.check('learner denied ' + verb + ' ' + target, not self.can(self.client, self.ns, verb, target))
            denied = self.oc('get', 'pods', '-n', 'default', config=self.client)
            self.check('foreign namespace access rejected', denied.returncode != 0 and 'Forbidden' in denied.stderr)
            for generation in [1, 2]:
                self.command('learner applies supplied workload', 'apply', '-f', '-', '-n', self.ns,
                             data=self.workload, config=self.client)
                self.command('learner exposes deployment', 'expose', 'deployment', 'web', '-n', self.ns,
                             '--port=8080', '--target-port=8080', config=self.client)
                self.command('learner creates edge Route', 'create', 'route', 'edge', 'web', '-n', self.ns,
                             '--service=web', '--port=8080', '--insecure-policy=Redirect', config=self.client)
                self.host = self.get('get', 'route', 'web', '-n', self.ns)['spec']['host']
                self.healthy()
                self.fault_and_repair(imperative=generation == 2)
                if generation == 1:
                    self.patch('service', {'spec': {'selector': {'app': 'missing'}}})
                    self.check('wrong selector rejected', not self.backend())
                    self.patch('service', {'spec': {'selector': {'app': 'web'}}})
                    self.patch('service', {'spec': {'ports': [{'port': 8080, 'targetPort': 9090}]}})
                    self.check('wrong target port rejected', not self.backend())
                    self.patch('service', {'spec': {'ports': [{'port': 8080, 'targetPort': 8080}]}})
                    self.patch('route', {'spec': {'to': {'kind': 'Service', 'name': 'missing'}}})
                    self.check('wrong Route backend rejected', not self.route())
                    self.patch('route', {'spec': {'to': {'kind': 'Service', 'name': 'web'}}})
                    self.healthy()
                    # A resource-only reset proof, not API generation/result enforcement.
                    for kind in ['route', 'service', 'deployment']:
                        self.command('reset deletes owned ' + kind, 'delete', kind, 'web', '-n', self.ns,
                                     '--wait=true', '--timeout=60s')
                        absent = self.oc('get', kind, 'web', '-n', self.ns)
                        self.check('reset confirms absent ' + kind, absent.returncode != 0 and 'NotFound' in absent.stderr)
                    self.check('reset preserves operator quota', self.get('get', 'resourcequota', 'outer-budget', '-n', self.ns)['spec']['hard']['pods'] == '4')
            self.report['limitations'] = ['Not a production evaluator or lifecycle service',
                'API stale-result, reward deduplication, progression and TTL enforcement not tested',
                'No simulated outage is counted as live infrastructure-error handling',
                'Temporary scoped diagnostic permissions; labs #2 integration pending']
    return Foundations


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
