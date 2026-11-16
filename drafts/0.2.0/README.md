# OpenShift foundations draft 0.2.0

Work for [content #4](https://github.com/SysKata-project/content/issues/4).
This is original SysKata material for a bounded DO180-aligned pilot, not a course
reproduction, certification assessment or released curriculum bundle.

| Lesson | Outcome | Estimate | Exercises |
| --- | --- | --- | --- |
| [oc-orientation](oc-orientation.md) | Identify project scope | 8 min | 4 |
| [oc-observe](oc-observe.md) | Diagnose with state and events | 10 min | 4 |
| [oc-workloads](oc-workloads.md) | Deploy and repair a rollout | 12 min | 4 |
| [oc-network](oc-network.md) | Trace Service/Route reachability | 10 min | 4 |

Estimates include explanation and practice; they are author estimates, not measured
learner timings. Shell/container prerequisites precede the first lesson. Stable
lesson, unit, journey and skill IDs follow the accepted objective map. Each lesson
has four exercises with hints, misconception feedback and positive/negative cases.
Command exercises explicitly describe their literal matching limits.

[Checkpoint A](checkpoint/README.md) adds a 20–25 minute practical task, a supplied
[workload](checkpoint/web.yaml), operator-only [fault patch](checkpoint/fault.patch.yaml)
and [scenario specifications](checkpoint/scenario-cases.json), including manifest
and imperative repair paths, wrong selectors/ports, stale evidence, infrastructure
failure, reset and cleanup. The scenarios have **not** been executed on a cluster.

## Compile and validate

From the repository root, with the documented Python 3.13 environment:

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/validate_sources.py
.venv/bin/python scripts/compile_bundle.py build drafts/0.2.0/catalog.yaml \
  --cases drafts/0.2.0/assessment-cases.json --output dist/foundations-draft
```

Choose a fresh output directory for each build; the compiler refuses to overwrite
an existing version. CI now discovers draft sources and runs schema, graph,
assessment-case and live reference checks on them. The compiler emits separate
learner and assessment artifacts with `release_eligible: false`. Only the four
text lessons are in this draft catalog. The checkpoint contract remains separate
until its real adapter can be compiled; no fixture lab evaluator is substituted.
Do not publish or activate this partial journey or use it to unlock administration.

## Verification and outstanding work

Local verification on 2026-11-16: 33 unit tests passed; the draft's 16 exercise
fixture sets passed schema/graph/evaluator compilation; all four official
`enterprise-4.22` documentation-source URLs returned HTTP 200 with TLS verification.
These source links use the accepted 4.22 baseline. They do not establish runtime
compatibility. `tested_versions` remains empty.

Content #4 cannot be marked ready or closed yet:

- Obtain access to the supported OpenShift allocation and run the checkpoint
  scenarios as the actual scoped learner, including alternate repair, reset and
  cleanup. The previous temporary kubeconfig was unavailable in this session.
- Integrate the required scoped reads and lifecycle protection through
  [labs #2](https://github.com/SysKata-project/labs/issues/2); the feasibility
  role alone is insufficient for all authored diagnosis commands.
- Integrate a production checkpoint adapter, profiles and evidence validation
  through [labs #3](https://github.com/SysKata-project/labs/issues/3), then represent
  the checkpoint as a real versioned lab exercise and compile the complete content.
- Verify API progression cannot bypass trusted checkpoint A success before
  `oc-declarative`, as required by the accepted journey map.

These are unresolved acceptance/integration work, not waived requirements. The
existing compiler release gate remains unchanged. Runtime evidence, final review,
approval and merge are still required; no curriculum release has been published.
