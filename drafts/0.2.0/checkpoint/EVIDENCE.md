# Foundations runtime proof — 2026-11-17

The scoped curriculum proof passed **78 checks** on **OpenShift 4.22.22**, followed
by verified cleanup. [Sanitized report](evidence/2026-11-17-foundations.json).
Executed proof source: `a2024bfc314563210479574f31653fe748388d8e`, proof version 1.
The report pins the script, workload and fault-patch bytes by SHA-256 and records
the public image digest. Follow the [reproduction runbook](VALIDATION.md).

The user supplied an existing ephemeral Red Hat workshops allocation and privately
authenticated its operator kubeconfig. The user accepted insecure API TLS for that
allocation; the proof inherited that API setting. **Route probes used normal TLS
verification** and verified the expected empty-directory HTTP response. No paid
infrastructure was provisioned and no runtime credentials or allocation hostnames
are committed.

The learner performed apply/expose/Route creation, rollout observation, event
inspection, pod description and repair under a temporary scoped service account.
The operator established isolation, injected the fault, observed evidence and
performed reset/cleanup. Operator access was not substituted for learner commands.
The tested workload used `restricted-v2`, assigned non-root UIDs, disabled automatic
service-account token mounting and dropped capabilities. The temporary learner
role includes the necessary diagnostic reads; production adoption belongs to labs #2.

The manifest and imperative repair paths each recorded Deployment generations
`1 -> 2 -> 3` with a stable UID within that attempt. Generation 2 had the controlled
image-pull failure; an older ready replica was not accepted as proof of repair.
The resource reset removed the first workload/Service/Route and preserved the
outer quota before the second attempt. Cleanup verified the owned namespace and
run-specific admission resources absent. This is not a test of API reset counters.

## Scenario coverage

| Specified case | Evidence in this change |
| --- | --- |
| manifest-repair | Live success, current rollout, backend and TLS-verified response |
| imperative-repair | Live alternate solution with the same outcome checks |
| old-replica | Live controlled failure rejected despite older availability; offline stale-status tests |
| wrong-selector | Live Service mutation rejected by backend predicate |
| wrong-port | Live target-port mutation rejected by backend predicate |
| wrong-route | Live Route target mutation rejected |
| no-tls | Live unsecured Route mutation rejected |
| fake-response | Not executed; production adapter must verify complete resource linkage |
| skipped-fault | Offline predicate rejects a fault snapshot without the deliberate image; production stage storage pending |
| recreated-deployment | Offline changed-UID rejection; no live delete/recreate grading claim |
| foreign-namespace | Actual scoped learner read against another namespace was Forbidden; production evidence binding pending |
| stale-generation | Offline non-increasing Deployment-generation rejection only; API lab-generation rejection pending |
| registry-outage | Production failure classification/delivery pending; no fabricated outage evidence |
| router-outage | Production failure classification/delivery pending |
| expired-access | Separate feasibility token-expiry test; production gateway expiry and outcome delivery pending |
| reset | Live resource reset, absence and quota preservation; API result invalidation pending |
| cleanup | Live ownership-checked namespace/admission cleanup |

The authored text catalog compiles with all **60 cases** for **16 exercises**.
The local suite has **36 tests**, including evidence rejection tests. Runtime
proof does not turn those specifications into a production evaluator. Per the
[owner's accepted decision](../DECISIONS.md), content can enter review with this
curriculum evidence while production evaluator integration and activation remain
gated on labs #3. The draft remains non-release eligible. No full DO180/DO280
coverage, production lifecycle readiness or complete journey is claimed.

## Replacement-cluster isolation

The [feasibility report](evidence/2026-11-17-feasibility.json) records all 33 checks
passing on 4.22.22, including cross-project API/network denial, privilege/token
restrictions, quotas, supplied-identity RBAC and actual expired-token rejection,
followed by verified cleanup. It used the unchanged pinned labs harness described
in the runbook. The second feasibility namespace was ownership-checked and removed
after its checks completed; its freed slot allowed the checkpoint proof to run
while the first identity remained alive for expiry testing. No more than two
namespaces were active at once. The harness subsequently verified both namespaces
absent and removed its admission binding/policy. No finalizers or shared cluster
settings were changed. An initial local invocation could not locate `oc`; no cluster
resources were created by that invocation, and the corrected PATH run is the report
published here.
