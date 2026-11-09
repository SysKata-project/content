# OpenShift objective coverage map

This map implements [content #3](https://github.com/SysKata-project/content/issues/3).
Every row uses source baseline **OpenShift 4.22**, reviewed **2026-11-04** and
rechecked **2026-11-09**. Sources: the public
[DO180 outline](https://www.redhat.com/en/services/training/red-hat-openshift-administration-i-operating-a-production-cluster)
and [DO280 outline](https://www.redhat.com/en/services/training/red-hat-openshift-administration-ii-configuring-a-production-cluster).
Rows paraphrase their objective areas; each skill and lesson is an original
SysKata planning allocation. The [journey](openshift-path.md) defines the seven
pilot lessons, checkpoint IDs, prerequisites and runtime evidence limits.

Environment codes:

- **P**: scoped pilot project, supplied identities, operator ceiling and isolation.
- **E**: future restricted environment/profile extension; unavailable in the current pilot.
- **D**: separately isolated environment and explicit operating/safety decision;
  unavailable on the shared pilot cluster, even with administrator installation access.

**Pilot** denotes selected scope, not availability or validation. **Planned**
rows are unavailable and outside the pilot. No row is **validated** yet. For a
partially covered source area, the gap is explicit; the pilot status applies only
to the named subset. IDs starting `oc-` in planned rows reserve future lessons,
not additional pilot lessons. A skill may contribute to several source areas.

## DO180 areas

| Area | Skill IDs | Lesson IDs | Scope and environment | Status / assessment evidence |
| --- | --- | --- | --- | --- |
| Platform concepts | `skill.oc.context` | `oc-orientation` | Project/resource context (P); console-wide monitoring remains a gap | Pilot subset; A context checks pending |
| CLI/API observation | `skill.oc.observe` | `oc-observe` | Namespaced diagnosis (P); cluster health operations excluded | Pilot subset; A diagnosis pending |
| Containers and pods | `skill.oc.pods` | `oc-pods` | Standalone pod lifecycle (E); distinct from managed workloads | Planned; none |
| Managed workloads and connectivity | `skill.oc.rollout`, `skill.oc.reachability` | `oc-workloads`, `oc-network` | Deployment, Service, Route (P) | Pilot; A deployment/reachability pending |
| Configuration and persistence | `skill.oc.configuration`, `skill.oc.storage` | `oc-configuration`, `oc-storage` | Configuration and persistent data (E); no learner secret access under current profile | Planned; none |
| Workload resilience | `skill.oc.resilience` | `oc-resilience` | Availability and scaling (E) | Planned; rollout repair alone does not cover this |
| Reproducible application changes | `skill.oc.rollout`, `skill.oc.updates` | `oc-workloads`, `oc-updates` | Failed rollout repair (P); broader update/rollback practice (E) | Pilot subset / planned remainder; A repair pending |
| Integrated review | `skill.oc.foundations-review` | `oc-foundations-review` | Full-area synthesis after broader coverage (E) | Planned; A assesses only the bounded slice |

## DO280 areas

| Area | Skill IDs | Lesson IDs | Scope and environment | Status / assessment evidence |
| --- | --- | --- | --- | --- |
| Declarative workflows | `skill.oc.manifests`, `skill.oc.parameterization` | `oc-declarative`, `oc-parameterization` | Manifest editing (P); environment parameterization (E) | Pilot subset / planned remainder; B manifests pending |
| Packaged deployments | `skill.oc.packages` | `oc-packages` | Package installation and updates (E) | Planned; none |
| Identity and permissions | `skill.oc.scoped-access`, `skill.oc.identity` | `oc-rbac`, `oc-identity` | Supplied-identity roles (P); identity-provider administration (D) | Pilot subset / planned remainder; B allow/deny pending |
| Traffic protection | `skill.oc.network-policy` | `oc-network-policy` | Author and verify network restrictions (E); operator-owned in pilot | Planned; infrastructure isolation proof is not learner evidence |
| Non-ingress exposure | `skill.oc.external-services` | `oc-external-services` | Alternative external service access (D) | Planned; unavailable pending network/cost decision |
| Tenant self-service | `skill.oc.budgets`, `skill.oc.self-service` | `oc-budgets`, `oc-self-service` | Exercise quota (P); project provisioning policy (D) | Pilot subset / planned remainder; B quota pending |
| Operator lifecycle | `skill.oc.operators` | `oc-operators` | Operator administration (D) | Planned; unavailable |
| Elevated application permissions | `skill.oc.privileges` | `oc-privileges` | Privileged workload configuration (D) | Planned; unavailable |
| Platform upgrades | `skill.oc.cluster-updates` | `oc-cluster-updates` | Cluster maintenance (D) | Planned; unavailable |
| Integrated review | `skill.oc.administration-review` | `oc-administration-review` | Full-area synthesis (D) | Planned; B assesses only the bounded slice |

## Planned skill meanings

Pilot skills are defined by the measurable outcomes in the journey. Remaining
IDs reserve these distinct meanings, rather than broad claims of mastery:

| Skill suffix after `skill.oc.` | Observable future outcome |
| --- | --- |
| pods | Diagnose the lifecycle of a standalone pod |
| configuration | Change external application configuration and verify consumption |
| storage | Attach persistent storage and verify data survives workload replacement |
| resilience | Configure and verify workload availability under a controlled failure |
| updates | Perform and verify a reproducible application update and recovery |
| foundations-review | Combine the full planned foundations skill set in a new scenario |
| parameterization | Produce equivalent manifests for different target environments |
| packages | Install and update a packaged application reproducibly |
| identity | Configure an identity provider and verify authentication behavior |
| network-policy | Demonstrate permitted and denied application traffic after a policy change |
| external-services | Verify controlled external reachability without the standard route path |
| self-service | Enforce project provisioning and tenant defaults |
| operators | Install and update an operator with observed lifecycle state |
| privileges | Justify and constrain an application's exceptional permissions |
| cluster-updates | Execute a platform update with workload continuity checks |
| administration-review | Combine the full planned administration skill set in an isolated scenario |

Future lesson prerequisite graphs are not approved by this mapping; author them
when expanding scope. They must build on relevant pilot skills and pass schema
reference/cycle validation. The seven-lesson pilot graph is fully specified now.

## Coverage claims

Neither checkpoint covers all rows. A covers four selected foundations skills;
B covers three selected administration skills. The broader source areas above
remain visible so that pilot completion cannot be mistaken for complete DO180
or DO280 coverage. Authoring and runtime validation remain in content #4/#5 and
labs #2/#3; expansion is tracked in content #6. Do not generate a released catalog
from this planning table or mark a row validated solely because a source URL works.
