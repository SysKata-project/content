# Apply and verify manifests

Outcome: apply a manifest change and verify desired and observed resource state.
Allow about 12 minutes including four practice exercises. Complete foundations,
trusted checkpoint A, and YAML editing prerequisites first. This lesson is an
original, bounded DO280-aligned pilot slice, not complete course coverage.

A manifest records desired state. Its `apiVersion` and `kind` identify the API
resource, `metadata.name` identifies the object, and `spec` describes the intended
configuration. A Deployment controller reconciles its pod template and replica
count asynchronously. A successful API response does not establish readiness.

Read the project assigned by your lab and confirm `oc project -q`. Inspect
`oc get deployment web -o yaml` before changing it. Keep the supplied workload's
image digest, resource requests/limits, and security settings. Change only the
fields requested by the exercise. Run `oc apply -f web.yaml` in the assigned
project. YAML indentation is structural; a field at the wrong level can be
rejected or fail to express the intended configuration.

Use `oc rollout status deployment/web --timeout=60s` and inspect the resulting
Deployment. Verify the controller observed the latest generation and that the
updated and ready replicas match the desired count. A ready pod from an older
revision is insufficient evidence. On failure, inspect conditions and events;
network/API failures are infrastructure problems, not wrong learner answers.

`oc create` creates a new object and usually fails if it already exists. `oc apply`
can reconcile a previously applied object. Reapplying an unchanged file should
preserve its intended state. If you imperatively change a field that the file
still specifies differently, a later apply can restore the file's value. Record
intentional changes in the manifest and verify actual state after every update.

Checkpoint B accepts equivalent manifest layouts producing the requested state;
it does not grade YAML key order. The short command exercises deliberately use
literal command matching, so their prompt specifies the requested spelling.

Review: explain why “configured” and “latest rollout ready” are different claims.

Reference: [OpenShift 4.22 object management](https://github.com/openshift/openshift-docs/blob/enterprise-4.22/cli_reference/openshift_cli/developer-cli-commands.adoc).
