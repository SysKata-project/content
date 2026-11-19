# Set and diagnose a resource budget

Outcome: configure an exercise quota within an operator ceiling and explain an
admission denial. Estimate: 12 minutes and four exercises. Complete `oc-rbac`
first. This is a small namespace-scoped administration exercise, not full
capacity planning or complete DO280 coverage.

A ResourceQuota limits aggregate usage in a namespace for the resources it names.
`spec.hard` describes the limits; `status.used` describes accounted usage. It does
not reserve capacity or ensure that a pod can be scheduled. CPU and memory
requests guide scheduling; limits bound container resource use. A LimitRange,
which can supply defaults or per-object constraints, is a different resource.

The operator owns `outer-budget`: 500m CPU and 512Mi memory requests, 1 CPU and
1Gi memory limits, and four pods. You cannot modify or delete it. The exercise
owns a separate quota named `exercise-budget`, with `hard.pods: "1"`. Both apply
at the same time: a second quota does not add capacity or override the first.

Apply your exercise quota, then inspect `oc describe resourcequota exercise-budget`.
Wait until its status reflects the intended hard limit. With one existing pod,
a request to create a second pod should fail with `exceeded quota` naming
`exercise-budget`. The controlled probe has valid security and resource fields,
so a different rejection is not evidence that this quota is correct.

A quota rejection can be reported as Forbidden even when the caller has RBAC
permission to create pods. Read the reason before changing permissions. Do not
solve the exercise by raising the outer ceiling, deleting isolation policies,
or adding a broader role. In real operations, reduce use or request an authorized
budget adjustment; here the assignment intentionally requires a one-pod quota.

A one-pod quota can prevent a rolling update that needs a temporary surge pod.
For checkpoint B, finish and verify the manifest update before imposing the
one-pod quota. During reset, the operator removes the exercise quota before
recreating the workload, while retaining the outer ceiling and isolation rules.
This ordering prevents an expected admission limit from masquerading as a broken
image or network error.

Review: explain why a quota of one plus a quota of four still rejects a second
pod, and distinguish that denial from RBAC denial and API unavailability.

Reference: [OpenShift 4.22 project quotas](https://github.com/openshift/openshift-docs/blob/enterprise-4.22/applications/quotas/quotas-setting-per-project.adoc).
