# Grant scoped read access

Outcome: grant a supplied identity pod read access in one project and verify
allowed and denied actions. Estimate: 12 minutes and four exercises. Complete
`oc-declarative` first. This is namespace-scoped pilot practice, not cluster-wide
identity administration or complete DO280 training.

Authentication establishes an identity; authorization decides which operations
that identity may perform. A namespaced Role contains API groups, resources and
verbs. For core pods, the API group is the empty string, the resource is `pods`,
and a minimal reader needs `get` and `list`. No wildcard, secret read or mutation
permission is needed. A RoleBinding connects that Role to a specific subject.

The operator supplies the ServiceAccount `supplied-reader` in your assigned
project. You do not create its credentials. In a RoleBinding subject, use kind
`ServiceAccount`, the exact name and its supplied namespace. In `roleRef`, use
API group `rbac.authorization.k8s.io`, kind `Role` and the name of your reader
Role. Create both using manifests in the assigned project. Changing a binding's
`roleRef` requires replacement; do not assume an apply can mutate that field.

A Role alone grants nobody access. A correct Role with the wrong binding subject
also fails the task. Conversely, adding a narrow Role does not revoke permissions
from another binding: RBAC grants are additive. The trusted test checks effective
access, including negative cases, rather than accepting resource names alone.

`oc auth can-i delete pods` checks your current identity in the selected project.
It does not prove what `supplied-reader` can do. The trusted operator tests the
supplied identity separately: pod list succeeds, while pod deletion, secret
reads and cross-project pod lists are denied. Its short-lived credential stays
outside your terminal. Do not request impersonation or use administrator
credentials to make a learner command succeed.

The lab permits creating only grants that pass Kubernetes escalation checks.
Binding cluster-admin, reading secrets, issuing tokens and changing the outer
isolation controls remain outside the exercise. A timeout is not proof of denial:
a negative access test requires an authorization rejection.

Review: identify the Role, binding and exact subject, then name one allowed and
three denied operations that would demonstrate the requested boundary.

Reference: [OpenShift 4.22 RBAC](https://github.com/openshift/openshift-docs/blob/enterprise-4.22/authentication/using-rbac.adoc).
