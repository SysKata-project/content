# OpenShift journey: DO180 and DO280 alignment

Status: initial curriculum plan, 2026-11-04. No lessons or lab compatibility have been validated yet.

## Sources and versions

Use the public [DO180 outline](https://www.redhat.com/en/services/training/red-hat-openshift-administration-i-operating-a-production-cluster) and [DO280 outline](https://www.redhat.com/en/services/training/red-hat-openshift-administration-ii-configuring-a-production-cluster), reviewed 2026-11-04. Both pages identify OpenShift 4.22. Record 4.22 as the source baseline, with an independently tested runtime version before release.

Author original scenarios and explanations aligned to these objectives. Do not reproduce proprietary course chapters, course lab solutions or exam questions. This journey is independent training and does not certify course equivalence or exam readiness.

## Pilot units

| ID | Focus | Alignment | Gate |
| --- | --- | --- | --- |
| oc-orientation | Resources, cluster context and projects | DO180 | Shell/container prerequisite guidance |
| oc-observe | oc queries, status, events and diagnosis | DO180 | Orientation |
| oc-workloads | Deployments and failed rollouts | DO180 | Observation |
| oc-network | Services/routes and application reachability | DO180 | Workloads |
| oc-declarative | Create and update resources from manifests | DO280 | Foundations checkpoint |
| oc-rbac | Namespaced roles and supplied identities | DO280 | Declarative basics |
| oc-budgets | Quotas and workload separation | DO280 | Scoped authorization |

Each lesson needs 3–5 short choice/ordering/command exercises, an explanation, feedback for likely mistakes, hints and version-matched official documentation. Pilot checkpoint A deploys/exposes/repairs an application; checkpoint B applies manifests, scoped RBAC and a quota, verifying both allowed and denied behavior. Each uses observable checks and a distinct scenario on the common lab platform.

The prerequisites unlock this bounded slice; completing four foundations lessons is not proof of full DO180 proficiency. Avoid cluster-admin operations in shared pilot environments. Preconfigure identities for scoped RBAC.

## Coverage backlog

Maintain an objective matrix with skill IDs, lesson IDs, source date/version, assessment evidence, environment needs and status (pilot/planned/validated). Extend foundations into configuration/storage, resilient workloads and broader update/recovery cases. Extend administration into identity management, packaged applications, network policy, external connectivity, self-service, Operators, elevated workload privileges and cluster maintenance. Cluster-wide operations need a separately isolated environment and cost decision before hands-on publication.

Do not show planned topics as completed or available. The MVP delivers seven lessons and two checkpoints, not full coverage of both course outlines. Keep future objective mapping in the same journey to avoid a disconnected second content model.
