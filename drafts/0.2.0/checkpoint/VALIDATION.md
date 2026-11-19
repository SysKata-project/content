# Running the curriculum proof

`scripts/validate_foundations.py` is an operator-triggered proof for the authored
checkpoint. It is not the production lab evaluator, terminal gateway or lifecycle
service. It does not release or activate content. Run the replacement-cluster
feasibility checks first. Normally run this proof after cleanup. If only token
expiry remains, the completed second feasibility namespace may be ownership-checked
and deleted before starting this one-namespace proof; retain the first namespace
and its identity for the expiry test. Never exceed two concurrent namespaces.
Both reports must pass, including cleanup, before accepting the runtime evidence.

Use Python 3.13 with the content repository dependencies, `oc` and `curl` in PATH,
and an authenticated private kubeconfig outside every checkout. Keep command
tracing disabled. No credentials are printed or included in the report. The API
uses the supplied kubeconfig's TLS configuration; route probes independently
require normal HTTPS certificate verification and provide no insecure override.

The script reuses the reviewed labs feasibility module from labs commit
`db614972bf5de9917726945b3a68e769680d6508`, guarded by SHA-256
`53fdfe51dcb658265c60e001827e5db01df0c7b068180ca9635568c2edac9534`.
It refuses changed module bytes before importing them. A new dependency revision
requires code review and renewed isolation testing; do not simply replace the
hash to suppress a mismatch.

From the content repository, with the labs checkout alongside it:

```sh
.venv/bin/python scripts/validate_foundations.py \
  --feasibility-harness ../labs/scripts/validate-openshift.py \
  --kubeconfig /private/tmp/syskata-private/cluster.kubeconfig \
  --report /private/tmp/syskata-private/foundations-report.json
```

The operator must be allowed to create a uniquely labeled namespace, quota,
network policy, service account, Role/RoleBinding, TokenRequest and a run-specific
ValidatingAdmissionPolicy/binding. The admission policy selects only the run's
namespace. The learner gets a ten-minute scoped token and permissions for the
lesson's application resources and diagnostic reads. No learner secrets, token
issuance, cluster-wide reads, quota or network-policy edits are permitted. This
is a temporary proof role, not a change to the labs #2 production contract.

The script executes the supplied deployment and exact Service/Route commands as
the learner; validates the current rollout, ready backend and HTTPS response;
records a controlled image-pull failure; and proves both manifest and imperative
repair against the same Deployment UID at later generations. It checks wrong
selectors, wrong ports and wrong Route targets, and tests a resource reset before
repeating the sequence. It does not simulate API result-delivery/generation logic.
The proof's snapshot predicates are not advertised as hardened grading adapters.

One namespace is created, within the existing 500m/512Mi request, 1 CPU/1Gi limit
and four-pod ceiling. An ownership-checked `finally` cleanup deletes that namespace
and verifies NotFound, then removes only the matching run-owned admission resources.
If cleanup fails, the admission protections remain. Use the recorded run ID to
inspect surviving resources; never delete unlabelled/shared objects or strip
finalizers. Temporary scoped kubeconfigs are removed on normal exit. A hard kill
or host failure still requires operator cleanup as described in the labs
[feasibility runbook](https://github.com/SysKata-project/labs/blob/main/docs/feasibility.md).

A report includes source commit and SHA-256 hashes for the executed proof and
manifests, runtime, checks, repair generations, limitations and cleanup outcome.
Only publish it after review and secret scanning. A successful proof does not
establish production evaluator compatibility, API progression, result replay
protection, automated lifecycle reset/TTL behavior or infrastructure-error delivery.
Those remain explicitly unverified integration requirements.
