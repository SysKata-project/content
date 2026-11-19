# Administration runtime evidence

On 2026-11-19, the scoped curriculum proof passed on **OpenShift 4.22.22**.
This validates the bounded content #5 checkpoint under the [accepted review
boundary](../DECISIONS.md), not a production evaluator, lifecycle service or
released curriculum. No adjustment to the OpenShift 4.22 source baseline was
needed for the operations tested.

## Provenance and results

- [Administration report](evidence/2026-11-19-administration.json): **102 checks
  passed**, followed by verified cleanup of owned namespaces and admission
  resources. Both the standard and alternate split-rule Role paths passed.
- [Replacement-cluster feasibility report](evidence/2026-11-19-feasibility.json):
  **33 checks passed**, followed by verified cleanup. Runtime: 4.22.22 with
  OVN-Kubernetes. The short-lived credential was rejected 65.55 seconds after its
  declared expiration, while its identity and RBAC were still present.
- Tested content source: `c5ba3da544dbfd9608fca460b1a1704e8c6b175d`.
  The administration report records SHA-256 fingerprints of the actual proof
  scripts, workload/RBAC/quota manifests and scenario specification. Those inputs
  remain unchanged in this evidence update. The scenario JSON retains its
  pre-run `specified-not-executed` metadata as a fingerprinted input; this report
  supplies execution status instead of rewriting that historical specification.
- Reviewed labs harness SHA-256:
  `53fdfe51dcb658265c60e001827e5db01df0c7b068180ca9635568c2edac9534`.
  The content harness verifies this digest before importing it.
- The image digest is recorded in both reports and the supplied manifest.
  Credential material and kubeconfig remain outside Git and learner terminals.
  Sanitized reports passed secret scanning before inclusion.

The replacement allocation was tested sequentially: feasibility's two sessions
were removed before administration's learner and foreign-test namespaces were
created. The administration report's `concurrency: 1` denotes its one active
learner workload; the second namespace exists only for cross-project denial.
The existing two-session ceiling and $0 incremental-cost scope were preserved.
No new infrastructure was purchased or provisioned outside the supplied cluster.

## Scenario evidence

| Criterion/scenario | Observed result |
| --- | --- |
| Desired manifest and latest observed rollout | Single updated ready replica and requested fields verified; reapply preserved Deployment UID |
| Wrong declared label | Rejected; correct manifest restored successfully |
| Unbound or wrong supplied identity | Pod read denied |
| Standard and alternate split-rule Role | Supplied identity could list pods and get a named pod |
| Negative effective-access checks | Pod deletion, secret reads and cross-project pod reads denied |
| Overbroad Role | Added delete permission detected; removing it restored denial |
| Escalation and outer ceiling | Cluster-admin binding and outer-quota patch rejected; outer quota unchanged |
| Exercise quota | One pod accounted; second valid pod rejected specifically by exercise-budget |
| Wrong quota | Two-pod quota rejected by the criterion; one-pod quota restored |
| Resource reset, twice | Exercise quota/binding/Role/Deployment and pods absent; reader access revoked; outer ceiling retained |
| Final cleanup | Owned namespaces and run-scoped admission policy/binding removed |
| Replacement-cluster boundary | Cross-project API/network denial, restricted verbs, token-mount restrictions, privileged-workload denial and credential expiry verified by feasibility proof |

The initial local feasibility invocation could not find `oc` on PATH and created
no cluster resources. It is not counted as a successful proof. The recorded
feasibility run used the installed binary explicitly on PATH. Both recorded live
runs completed without failed checks.

## Remaining integration boundaries

Offline rejection tests cover stale Deployment observations and distinguishing
API/authentication failures from authorization and quota denials. They do not
claim a live infrastructure-outage experiment.

Production evaluator delivery, instance/content/session-generation matching,
stale-result rejection, replay/reward deduplication, terminal/session TTL and
checkpoint unlock enforcement remain unverified and belong to labs/API integration.
The proof's resets establish resource cleanup and access revocation, not API
session-generation behavior. Neither checkpoint is activated by this text-only
draft. Labs #3 must integrate the real adapters before release; API integration
must require trusted A before administration and trusted B before pilot completion.
