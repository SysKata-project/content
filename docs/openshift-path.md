# OpenShift journey: DO180 and DO280 alignment

Status: curriculum mapping for [content #3](https://github.com/SysKata-project/content/issues/3),
2026-11-09. Seven lessons and two checkpoints are planned for the pilot; none is
released or validated as learning content. This is not full DO180/DO280 coverage,
course equivalence, certification, or a claim of exam readiness.

## Sources and versions

The public [DO180 outline](https://www.redhat.com/en/services/training/red-hat-openshift-administration-i-operating-a-production-cluster)
and [DO280 outline](https://www.redhat.com/en/services/training/red-hat-openshift-administration-ii-configuring-a-production-cluster)
are the objective sources. Preserve the original **2026-11-04 review baseline**,
**OpenShift 4.22**. The outlines were checked again on 2026-11-09 and still identify
4.22. The [objective map](openshift-objectives.md) covers each public outline area,
including areas outside the pilot. Its descriptions and skill design are original
SysKata material, not copied course lessons, lab solutions or exam questions.

Separately, [labs #1 feasibility evidence](https://github.com/SysKata-project/labs/blob/main/docs/feasibility.md)
records namespace-scoped proof tasks on **OpenShift 4.22.20**, dated 2026-11-06.
The ephemeral Red Hat workshops allocation permits two concurrent sessions at
$0 incremental cost using the existing allocation only. It is not a durable
provider commitment or a claim of zero underlying infrastructure cost. Replacement
clusters need fresh validation. No source-baseline adjustment was identified for
the tested operations; this does not validate every objective or the pilot lessons.

## Entry prerequisites

Before `oc-orientation`, learners should be able to navigate files in a Bash
shell, edit a text file, recognize arguments and exit status, and explain the
difference between a container image and a running container. They should know
basic process and network concepts: a process can fail, and a host and port
identify a network destination. Offer prerequisite guidance and practice when
these are unfamiliar; do not present the journey as introductory Linux training.
No prior cluster administrator access is needed.

Before the administration slice, learners also need to edit YAML safely, read
command output, and distinguish authentication from permission to perform an
operation. The foundations slice and checkpoint establish the relevant OpenShift
practice; completion does not establish all prerequisites for the full DO280
course. The public course recommends broader shell/network/security proficiency.

## Stable IDs and pilot sequence

Retain the existing `oc-*` plan IDs as lesson IDs; they were previously labeled
as units. Reserve `unit.oc-foundations` and `unit.oc-administration` for the two
actual units, and `journey.openshift` for the journey. These are planning IDs,
not released catalog entities. Skill IDs below have fixed meanings; do not reuse
an ID for a different skill. Follow [schema revision rules](content-schema.md)
when authoring and releasing entities.

| Lesson ID | Unit | Measurable outcome and skill ID | Required prior lesson | Additional gate |
| --- | --- | --- | --- | --- |
| `oc-orientation` | foundations | Identify the active project and distinguish project-scoped resources: `skill.oc.context` | None | Entry prerequisites |
| `oc-observe` | foundations | Use resource state and events to explain a workload symptom: `skill.oc.observe` | `oc-orientation` | None |
| `oc-workloads` | foundations | Deploy an application and repair a failed rollout: `skill.oc.rollout` | `oc-observe` | None |
| `oc-network` | foundations | Trace application reachability through a Service and Route: `skill.oc.reachability` | `oc-workloads` | None |
| `oc-declarative` | administration | Apply a manifest change and verify resulting resource state: `skill.oc.manifests` | `oc-network` | Trusted success for checkpoint A |
| `oc-rbac` | administration | Grant a supplied identity a scoped role and verify allowed/denied actions: `skill.oc.scoped-access` | `oc-declarative` | None |
| `oc-budgets` | administration | Configure an exercise quota within an operator ceiling and explain a denial: `skill.oc.budgets` | `oc-rbac` | None |

Each skill has the preceding row's skill as its direct prerequisite; the first
has none. Each lesson depends on the preceding lesson, as explicitly listed.
The administration unit depends on the foundations unit. Unit ordering alone
must not silently bypass the checkpoint gate.

Each lesson will contain an explanation, 3–5 choice/ordering/command exercises,
hints, misconception feedback, duration estimates and version-matched references.
Those authored assets and their positive/negative fixtures belong to
[content #4](https://github.com/SysKata-project/content/issues/4) and
[content #5](https://github.com/SysKata-project/content/issues/5).

## Checkpoints and prerequisite edges

| Stable checkpoint ID | Required lesson completion | Required checkpoint | Observable outcome | Skills assessed |
| --- | --- | --- | --- | --- |
| `checkpoint.oc-foundations` (A) | `oc-network` and its transitive prerequisites | None | Deploy and expose an application, diagnose and repair a failing rollout; verify reachable service and healthy workload | `skill.oc.context`, `skill.oc.observe`, `skill.oc.rollout`, `skill.oc.reachability` |
| `checkpoint.oc-administration` (B) | `oc-budgets` and its transitive prerequisites | A | Apply manifests, bind a scoped role to a supplied identity, and configure an exercise quota; verify both allowed and denied behavior | `skill.oc.manifests`, `skill.oc.scoped-access`, `skill.oc.budgets` |

The complete progression is:

```text
entry guidance -> oc-orientation -> oc-observe -> oc-workloads -> oc-network
  -> checkpoint.oc-foundations -> oc-declarative -> oc-rbac -> oc-budgets
  -> checkpoint.oc-administration -> bounded pilot completion
```

Checkpoints are lab exercises, not two extra lessons. The table specifies logical
unlock gates in addition to lesson prerequisites. Schema 1.0.0 lesson prerequisites
can refer only to lessons: do not put checkpoint IDs into that array or invent a
new entity kind. Preserve these gates in the content/API integration and retain
stable checkpoint IDs for trusted assessment and reward deduplication. The
mapping is planning metadata, not a new released schema or runnable catalog;
content #4/#5 and API session implementation must demonstrate that checkpoint A
cannot be bypassed when unlocking `oc-declarative`, and that B is required for
pilot completion.

Use the accepted [learning policy](https://github.com/SysKata-project/docs/blob/main/decisions/0002-learning-policy.md):
guided success can complete objectives, while independent skill evidence remains
separate. A lab objective needs trusted successful assessment, not simply opening
a terminal or viewing a solution. Infrastructure errors neither satisfy the gate
nor count as learner mistakes. Checkpoint rewards use the same stable IDs and
must not repeat on resets or replays. This mapping introduces no new XP policy.

## Environments and availability

The pilot uses a learner project with scoped, expiring access, supplied identities
and an operator-owned outer quota. Learners cannot change isolation policies,
issue credentials, read secrets, or acquire cluster-admin. An exercise quota must
not replace the outer ceiling. Evaluators run outside learner-controlled projects.
The feasibility profile is an input to labs #2; it is not an already implemented
terminal/lifecycle service. Detailed release evidence remains required.

Cluster identity configuration, shared self-service policy, Operators, cluster
updates and elevated workloads remain **unavailable** until a separately isolated
environment, operating budget and safety validation exist. Namespaces on the
shared cluster are not sufficient isolation for these tasks. The planned map
also marks narrower activities that need capabilities absent from the current
learner profile, such as storage and network-policy editing. No planned row is a
learner-selectable activity.

## Evidence and maintenance

In the objective map, **pilot** means selected for authoring, **planned** means
outside the bounded pilot, and **validated** requires evidence for the actual
lesson/checkpoint at its released content/evaluator version and tested runtime.
No row is currently validated. Runtime feasibility alone cannot change that.
Each release must link its assessment fixtures, runtime report and bundle version;
keep runtime `tested_versions` empty until the corresponding content is tested.

When public outlines change, record a new review date and compare objective rows;
do not silently rewrite the 2026-11-04 baseline. Update the map, lesson/skill edges
and authoring issues together. Check uniqueness, reference resolution and cycles
when the planning IDs become catalog entities. Released versions remain immutable.
Future coverage continues in the same journey under
[content #6](https://github.com/SysKata-project/content/issues/6).
