# Administration proof validation

Live status: **pending**. On 2026-11-19 the existing private kubeconfig could not
resolve the configured API hostname (DNS failure). No runtime version, passing checkpoint result or cleanup result is
claimed for this draft. A replacement authenticated private kubeconfig is needed.

From the content repository, run against the agreed ephemeral test cluster:

```sh
.venv/bin/python scripts/validate_administration.py \
  --feasibility-harness ../labs/scripts/validate-openshift.py \
  --kubeconfig /private/tmp/syskata-private/cluster.kubeconfig \
  --report /private/tmp/syskata-private/administration-report.json
```

The external harness must match its reviewed SHA-256; mismatches fail before
execution. Requirements and allowed operator privileges are in the checkpoint
README and labs feasibility guide. Confirm private kubeconfig authentication and
cluster connectivity first. Do not print credentials or raw command errors.
The script captures commands and emits bounded pass/fail labels and sanitized
resource/input fingerprints. Temporary learner credentials are deleted on exit.
Review and scan the report before committing any evidence.

Run the full labs feasibility proof on a replacement cluster before recording
administration compatibility. Record actual OpenShift version, source commit and
input digests, every scenario outcome and verified cleanup. Keep any failed run
explicitly distinct from passing evidence. The complete run must finish before
short-lived credentials expire; authentication expiry is a failed proof, not a
permission denial. Re-run after fixing its cause with fresh resources/credentials.

Offline tests exercise manifest state, stale-generation rejection, quota accounting,
error classification, compilation and assessment-answer separation. They do not
prove real authorization, admission, reconciliation, reset or cleanup. Scenario
cases describing API generation/replay remain integration requirements, not live
checks performed by this harness.
