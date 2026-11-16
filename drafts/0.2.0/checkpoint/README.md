# Foundations checkpoint A — authoring contract

Stable ID: `checkpoint.oc-foundations`, revision 1. Draft for content #4.
Estimated learner time: 20–25 minutes after the four foundations lessons.
No runtime validation or production evaluator integration is claimed.

## Learner task

In your assigned project, deploy the supplied `web.yaml`, expose its application
through a ClusterIP Service and an edge-terminated Route, and demonstrate its
expected response over HTTPS. Request the controlled fault stage, inspect why
the new rollout cannot complete, and repair it. Finish with the latest desired
replica ready and the application reachable. Use manifests or CLI commands;
assessment concerns outcomes, not a specific command sequence.

## Prerequisites and progression

Require completion of `oc-network` and its transitive lesson prerequisites.
Assess `skill.oc.context`, `skill.oc.observe`, `skill.oc.rollout` and
`skill.oc.reachability`. This checkpoint is a lab exercise, not a fifth lesson.
Trusted success is required before unlocking `oc-declarative`; opening a terminal,
finishing text exercises, revealing a solution, or a client success flag cannot
satisfy it. Guided success follows the existing learning policy. API/labs must
bind evidence to authenticated learner, lab session, checkpoint revision and reset
generation and deduplicate reward events by stable checkpoint ID.

## Operator setup contract

Use the namespace isolation profile proven in labs #1, with the additional
Service/Route, object-count and gateway restrictions required by labs #2 before
exposing a general learner terminal. Limit concurrency to two sessions on the
approved existing allocation; do not provision paid infrastructure. Replacement
clusters need renewed isolation validation. Provide an assigned project and
expiring scoped learner credentials; keep operator/evaluator credentials outside
it. Preserve fixed quota, network policy and admission controls. Do not copy the
feasibility harness unchanged into a production service.

The feasibility learner role does not yet grant event or ReplicaSet reads.
Labs #2 must provide scoped read access needed for pod-event diagnosis and
`oc rollout status`, and validate the exact commands as the learner identity.
Do not substitute operator access to claim that learner diagnosis was tested.
EndpointSlice inspection for assessment belongs to the trusted evaluator.

Supply `web.yaml` as a read-only starting file in the terminal. It uses the same
public image digest as the feasibility proof, an empty working directory and a
small Python HTTP server. The operator must validate the image/platform, assigned
UID support, registry access, route certificate chain and expected HTTP body on
this allocation before offering the task. No learner data is served. Initial
state has no web Deployment, Service or Route. Learners create those three objects;
operators supply the namespace and protective resources.

After trusted observation of the initial successful rollout and expected HTTPS
response, the controller records the Deployment UID and applies `fault.patch.yaml`
to that Deployment only. It must record the resulting failed generation and image
pull failure before asking for repair. The `.invalid` registry name makes the
fault deliberate and distinguishes it from an outage of the approved registry.
Do not count arbitrary network failures as the intended fault. An old replica
remaining available during the failed rollout is allowed and is not repair proof.

## Observable criteria and feedback

- **context:** Every observed resource belongs to the assigned session namespace
  and current generation. A same-named object elsewhere cannot satisfy the task.
- **deployment:** Deployment `web` has one desired replica, the approved image
  digest and required security/resource settings; the controller has observed its
  latest generation and that generation has one updated and ready replica with
  no unavailable replicas. Do not accept only an old available replica.
- **service:** Service `web` is ClusterIP with no external IPs, selects the web
  pods and maps port 8080 to their listening port 8080. Verify a ready EndpointSlice
  backend owned by the expected Service rather than trusting arbitrary endpoints.
- **route:** Route `web` is admitted, uses edge TLS, redirects insecure requests,
  targets Service `web` on port 8080 and uses the assigned platform host. A custom
  unrelated backend or another session's host fails.
- **response:** A TLS-verified HTTPS GET to that host returns 200 and the expected
  `Directory listing for /` marker with an empty file list from `/tmp/syskata-web`.
  Verify linkage through the inspected Route/Service/backend, not the body alone.
- **repair:** Trusted stage records show initial success, the deliberate broken
  generation and successful recovery at a later generation of the same Deployment
  UID. Recreating the Deployment to erase the fault history is not accepted; the
  learner can reset and repeat if it was deleted.

Hints should first direct learners to context and events, then image/template,
then Service selection and Route target. On rollout failure explain the difference
between an old available replica and the updated replica. On Service failure
explain labels/target ports. On Route failure explain admission/targeting. Reveal
may show applying the original supplied manifest, exposing the Deployment and
creating an edge Route; it must be recorded as assistance, not independent mastery.

## Reset, expiry and errors

Reset creates a new generation, invalidates outstanding assessments and earlier
stage evidence, removes only this session's workload/Service/Route, and restores
the pristine start. Preserve operator quotas/isolation. Use session-owned resource
labels plus expected names/UIDs before deleting; do not delete unrelated objects.
A lifecycle implementation may replace the whole owned namespace with a fresh
one. On TTL expiry revoke access and clean up the owned namespace through labs.
Never remove finalizers or shared protections just to force cleanup.

Registry, API, router or trusted evaluator failures produce retryable infrastructure
outcomes with no learner penalty and no success. Missing trusted evidence is
pending/error, never guessed. Retry assessments in the same generation; reject
stale generation results. Distinguish network errors from a verified NotFound.

## Fixtures and evidence boundary

`scenario-cases.json` specifies positive, negative and alternate-solution scenarios
for the production adapter in labs #3. These are scenario specifications, not
fabricated cluster observations or a new executable evaluator. The compiler's
production-lab release gate stays closed. The lesson-only draft compiles separately
with `release_eligible: false`; it cannot unlock administration or claim checkpoint
completion. Integrate this stable exercise into a versioned catalog only when its
real adapter, profiles, fixtures and evidence validator are available.

Before content #4 can be ready, record actual runtime version, source commit,
image digest, evaluator version, each scenario result, route/body verification,
failure/repair generations, reset isolation and verified cleanup. Keep credentials,
hostnames tied to private allocations and raw kubeconfigs out of Git. Keep runtime
`tested_versions` empty until that evidence exists. Source baseline remains 4.22;
feasibility on 4.22.20 from 2026-11-06 is not checkpoint validation.
