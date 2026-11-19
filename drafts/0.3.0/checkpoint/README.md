# Checkpoint B: scoped administration

Stable ID: `checkpoint.oc-administration`, revision 1. Estimate: 20–25 minutes.
Prerequisites: all seven pilot lessons through `oc-budgets`, trusted checkpoint A
success, YAML editing and authentication/authorization basics. This is original
SysKata material, a bounded DO280-aligned subset, not full course coverage.

Status: scoped runtime proof passed 102 checks on OpenShift 4.22.22 with verified
cleanup. No production evaluator or curriculum release is claimed. See
[evidence](EVIDENCE.md), [reproduction](VALIDATION.md) and the original pre-run
[scenario specification](scenario-cases.json).

## Learner task and observable criteria

Work only in the assigned project with the supplied scoped identity.

1. Apply the supplied [Deployment](web.yaml). Preserve its digest, single replica,
   resource requests/limits and security controls. The pod template must carry
   `exercise: administration`. Verify the current generation has one updated ready
   replica. Reapplying the manifest must preserve the Deployment identity.
2. Define a namespaced reader Role and bind it to the operator-supplied
   `supplied-reader` ServiceAccount in this project. Its effective access must
   allow `get` and `list` pods and deny deleting pods, reading secrets and listing
   pods in the separate test project. Do not create or expose its credential.
3. After the Deployment converges, apply `exercise-budget` with only `pods: "1"`.
   Verify its accounted hard limit and one used pod, then demonstrate a second
   valid pod request is rejected specifically by this quota. Keep the operator
   quota, network controls and service accounts unchanged.

[Role](reader-role.yaml), [binding](reader-binding.yaml) and
[quota](exercise-budget.yaml) are reference solutions for the operator/author;
production learner delivery must not expose completed RBAC/quota answers as
question payloads. Replace the binding's namespace placeholder with the assigned
project. The operator proof does this in memory. The workload is a supplied input,
not a requirement to invent application code or choose an image.

Assessment checks outcomes, not command history or YAML key order. A Role with
separate get/list rules is an alternate valid solution. Wrong subjects, stale
rollout status, widened permissions and a two-pod exercise quota fail their
respective criteria. Quota admission failure must name `exercise-budget`; an
RBAC denial, image failure or connection error is not quota proof.

## Setup and privileges

Reuse the reviewed labs feasibility harness pinned by digest. The operator
creates two uniquely labeled temporary namespaces, fixed outer quotas and network
policies, the admission boundary, and short-lived learner/supplied-reader
credentials. The second namespace supports a real cross-project denial check;
no workload is deployed there. The two-namespace allocation stays within the
existing two-session ceiling and provisions no paid infrastructure.

The operator owns the outer ceiling: 500m/512Mi requests, 1 CPU/1Gi limits and four
pods per namespace. The learner can manage its Deployment, pods, non-escalating
Roles/RoleBindings and `exercise-budget`; it cannot change the outer ceiling,
network policy, service accounts or credentials, impersonate identities, or grant
cluster-admin. The temporary proof role excludes exec, Services and Routes.
The proof uses the pinned UBI workload with no mounted service-account token,
assigned non-root UID, dropped capabilities and no privilege escalation.

Operator credentials remain outside the checkout and outside learner terminals.
The trusted proof issues the supplied identity's short-lived credential privately
and checks it directly. This does not implement a production terminal gateway.
A replacement cluster also needs the full labs feasibility/isolation validation.

## Reset, failure and integration

The operator removes the exercise quota first, then the exercise binding, Role
and Deployment. It waits for absence of the owned resources and pods, checks that
reader access was revoked, and verifies the outer ceiling remains. A second pass
uses equivalent split Role rules. The final cleanup removes only run-labeled
namespaces and, after namespace cleanup succeeds, the run-owned admission policy
and binding. On incomplete cleanup, retain isolation and follow the recovery
procedure in [labs feasibility](https://github.com/SysKata-project/labs/blob/main/docs/feasibility.md).

Production reset must create a new session generation and reject old assessments.
The proof's two passes demonstrate resource reset only. Authentication failure,
API outage or evaluator failure yields infrastructure failure, never a learner
mistake, completion or reward. Production labs/API integration must authenticate
results, bind them to instance/content/evaluator/session generation, deduplicate
replays and protect prerequisite gates. Checkpoint A must precede administration;
checkpoint B must precede bounded pilot completion. These integrations remain
with labs #2/#3 and API work under the [accepted boundary](../DECISIONS.md).
